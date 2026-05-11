from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import pytesseract
from PIL import Image
import tempfile
import os
import boto3
import torch
import torch.nn.functional as F
from transformers import LayoutLMForTokenClassification, LayoutLMTokenizerFast, LayoutLMTokenizer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Labels - must match training
label_list = [
    "O",
    "B-COMPANY", "I-COMPANY",
    "B-DATE", "I-DATE",
    "B-ADDRESS", "I-ADDRESS",
    "B-TOTAL", "I-TOTAL",
]
label2id = {l: i for i, l in enumerate(label_list)}
id2label = {i: l for l, i in label2id.items()}

S3_BUCKET = os.environ.get("S3_BUCKET", "cloudproject-invoices-015518371430")
MODEL_PATH = "/app/best_model.pt"

device = torch.device("cpu")
tokenizer = None
model = None

def download_model_from_s3():
    if os.path.exists(MODEL_PATH):
        print("Model already exists locally")
        return
    print("Downloading model from S3...")
    s3 = boto3.client("s3")
    s3.download_file(S3_BUCKET, "models/best_model.pt", MODEL_PATH)
    print("Model downloaded successfully!")

@app.on_event("startup")
async def startup_event():
    global tokenizer, model
    try:
        print("=== STARTUP BEGINNING ===")
        download_model_from_s3()
        print("=== LOADING TOKENIZER ===")
        tokenizer = LayoutLMTokenizerFast.from_pretrained(
            "microsoft/layoutlm-base-uncased"
        )
        print("=== LOADING BASE MODEL ===")
        model = LayoutLMForTokenClassification.from_pretrained(
            "microsoft/layoutlm-base-uncased",
            num_labels=len(label2id),
            id2label=id2label,
            label2id=label2id
        )
        print("=== LOADING FINE-TUNED WEIGHTS ===")
        if os.path.exists(MODEL_PATH):
            state = torch.load(MODEL_PATH, map_location=device)
            model.load_state_dict(state)
            print("=== FINE-TUNED WEIGHTS LOADED SUCCESSFULLY ===")
        model.to(device)
        model.eval()
        print("=== MODEL READY ===")
    except Exception as e:
        print(f"=== STARTUP ERROR: {e} ===")
        import traceback
        traceback.print_exc()

def normalize_box(box, w, h):
    x0, y0, x1, y1 = box
    return [
        int(1000 * x0 / w),
        int(1000 * y0 / h),
        int(1000 * x1 / w),
        int(1000 * y1 / h)
    ]

def preprocess_image(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    if w < 1000:
        scale = 1000 / w
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    # Skip deskew - causes incorrect rotation on real invoices
    return thresh

def deskew(image: np.ndarray) -> np.ndarray:
    coords = np.column_stack(np.where(image > 0))
    if len(coords) == 0:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    if abs(angle) < 0.5:
        return image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h),
                          flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)

def run_ocr(processed_image: np.ndarray):
    pil_image = Image.fromarray(processed_image)
    config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(pil_image, config=config)
    data = pytesseract.image_to_data(
        pil_image, config=config,
        output_type=pytesseract.Output.DICT
    )
    words = []
    boxes = []
    words_and_boxes = []
    for i in range(len(data['text'])):
        word = data['text'][i].strip()
        conf = int(data['conf'][i])
        if word and conf > 40:
            box = [
                data['left'][i],
                data['top'][i],
                data['left'][i] + data['width'][i],
                data['top'][i] + data['height'][i]
            ]
            words.append(word)
            boxes.append(box)
            words_and_boxes.append({"word": word, "box": box})
    return text, words, boxes, words_and_boxes

def predict(words, boxes, image_shape):
    h, w = image_shape[:2]
    proc_w = 1200
    proc_h = int(h * (proc_w / w))
    normalized_boxes = [normalize_box(b, proc_w, proc_h) for b in boxes]

    # Use slow tokenizer for boxes
    slow_tokenizer = LayoutLMTokenizer.from_pretrained(
        "microsoft/layoutlm-base-uncased"
    )
    encoding = slow_tokenizer(
        words,
        boxes=normalized_boxes,
        is_split_into_words=True,
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt"
    )

    # Use fast tokenizer for word_ids
    fast_encoding = tokenizer(
        words,
        is_split_into_words=True,
        truncation=True,
        padding="max_length",
        max_length=512
    )

    model_inputs = {
        k: v.to(device)
        for k, v in encoding.items()
        if k in ["input_ids", "attention_mask", "token_type_ids", "bbox"]
    }

    with torch.no_grad():
        outputs = model(**model_inputs)

    logits = outputs.logits
    probs = F.softmax(logits, dim=-1)
    conf, preds = torch.max(probs, dim=-1)

    return fast_encoding, preds[0].tolist(), conf[0].tolist()

def align_predictions(encoding, words, preds, conf, threshold=0.0):
    word_ids = encoding.word_ids(batch_index=0)
    results = []
    seen = set()

    for idx, word_idx in enumerate(word_ids):
        if word_idx is None:
            continue
        if word_idx in seen:
            continue
        seen.add(word_idx)

        pred = preds[idx]
        c = conf[idx]

        if pred >= len(id2label):
            continue

        label = id2label[pred]
        if label == "O":
            continue
        if c < threshold:
            continue

        word = words[word_idx]
        results.append((word, label, c))

    return results

def extract_fields(aligned):
    result = {"COMPANY": [], "DATE": [], "TOTAL": [], "ADDRESS": []}

    for token, label, _ in aligned:
        is_subword = token.startswith("##")
        token = token.replace("##", "")

        if "COMPANY" in label:
            result["COMPANY"].append((token, is_subword))
        elif "DATE" in label:
            result["DATE"].append((token, is_subword))
        elif "TOTAL" in label:
            result["TOTAL"].append((token, is_subword))
        elif "ADDRESS" in label:
            result["ADDRESS"].append((token, is_subword))

    def join_tokens(token_list):
        out = ""
        seen = set()
        for token, is_sub in token_list:
            if not is_sub and token in seen:
                continue
            seen.add(token)
            out = out + token if is_sub else (out + " " + token if out else token)
        return out.strip()

    return {k: join_tokens(v) for k, v in result.items()}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "model-api",
        "model_loaded": model is not None
    }

@app.post("/process")
async def process_invoice(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        img = cv2.imread(tmp_path)
        if img is None:
            return {"status": "error", "message": "Could not read image"}

        processed = preprocess_image(img)
        raw_text, words, boxes, words_and_boxes = run_ocr(processed)

        layoutlm_result = None
        if model is not None and words:
            encoding, preds, conf = predict(words, boxes, img.shape)
            aligned = align_predictions(encoding, words, preds, conf)
            fields = extract_fields(aligned)
            layoutlm_result = {
                "company_name": fields.get("COMPANY") or None,
                "date": fields.get("DATE") or None,
                "address": fields.get("ADDRESS") or None,
                "total_price": fields.get("TOTAL") or None
            }

        return {
            "status": "success",
            "raw_text": raw_text,
            "words_and_boxes": words_and_boxes,
            "layoutlm_extraction": layoutlm_result
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        os.unlink(tmp_path)
