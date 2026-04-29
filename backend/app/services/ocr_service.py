import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageOps, ImageFilter
import os

# Windows path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess_image(image: Image.Image) -> Image.Image:
    """Improve OCR accuracy"""
    image = image.convert("L")  # grayscale
    image = ImageOps.autocontrast(image)
    image = image.resize((image.width * 2, image.height * 2))
    image = image.filter(ImageFilter.SHARPEN)
    return image


def extract_text(file_path: str) -> str:

    ext = os.path.splitext(file_path)[1].lower()

    # Images
    if ext in [".png", ".jpg", ".jpeg"]:

        image = Image.open(file_path)
        image = preprocess_image(image)

        config = r'--psm 6'
        text = pytesseract.image_to_string(image, config=config)

        return text


    # PDF files
    elif ext == ".pdf":

        pages = convert_from_path(file_path, dpi=300)
        full_text = ""

        config = r'--psm 6'

        for page in pages:
            page = preprocess_image(page)
            full_text += pytesseract.image_to_string(page, config=config) + "\n"

        return full_text


    else:
        raise ValueError("Unsupported file type")