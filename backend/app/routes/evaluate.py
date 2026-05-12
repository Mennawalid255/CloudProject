from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
import requests
import os
import json
import boto3
import re

evaluate_bp = Blueprint("evaluate", __name__)

MODEL_API_URL = os.environ.get("MODEL_API_URL", "http://localhost:8000")
S3_BUCKET = os.environ.get("S3_BUCKET", "cloudproject-invoices-015518371430")

def word_level_f1(predicted, ground_truth):
    predicted_tokens = set(predicted.lower().split())
    gt_tokens = set(ground_truth.lower().split())
    if not predicted_tokens and not gt_tokens:
        return 1.0
    if not predicted_tokens or not gt_tokens:
        return 0.0
    intersection = predicted_tokens & gt_tokens
    precision = len(intersection) / len(predicted_tokens)
    recall = len(intersection) / len(gt_tokens)
    if precision + recall == 0:
        return 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return f1

def load_ground_truth():
    s3 = boto3.client("s3")
    obj = s3.get_object(
        Bucket=S3_BUCKET,
        Key="evaluation/ground_truth.json"
    )
    return json.loads(obj['Body'].read().decode('utf-8'))

@evaluate_bp.route("/evaluate/<filename>", methods=["GET"])
@jwt_required()
def evaluate_invoice(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        # Step 1 - Get extraction from model API
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{MODEL_API_URL}/process",
                files={"file": (filename, f)},
                timeout=120
            )

        model_result = response.json()

        if model_result.get("status") != "success":
            return jsonify({
                "status": "error",
                "message": "Model processing failed"
            }), 500

        # Step 2 - Get LayoutLM extraction
        layoutlm_result = model_result.get("layoutlm_extraction", {})
        raw_text = model_result.get("raw_text", "")

        predicted = {
            "COMPANY": layoutlm_result.get("company_name") or "",
            "DATE": layoutlm_result.get("date") or "",
            "ADDRESS": layoutlm_result.get("address") or "",
            "TOTAL": layoutlm_result.get("total_price") or ""
        }

        # Step 3 - Load ground truth
        ground_truth = load_ground_truth()

        # Check if this invoice has ground truth
        base_filename = os.path.basename(filename)
        # Try to match by original filename
        gt = None
        for key in ground_truth:
            if key.lower() in base_filename.lower() or base_filename.lower() in key.lower():
                gt = ground_truth[key]
                break

        if not gt:
            # No ground truth available - return predictions only
            return jsonify({
                "status": "success",
                "mode": "prediction_only",
                "predicted": predicted,
                "raw_text": raw_text,
                "message": "No ground truth available for this invoice"
            }), 200

        # Step 4 - Calculate F1 scores
        fields = ["COMPANY", "DATE", "ADDRESS", "TOTAL"]
        field_results = {}
        total_f1 = 0
        label_correct = 0

        for field in fields:
            pred_value = predicted.get(field, "")
            true_value = gt.get(field, "")

            f1 = word_level_f1(pred_value, true_value)
            total_f1 += f1

            if pred_value:
                label_correct += 1

            field_results[field] = {
                "predicted": pred_value,
                "ground_truth": true_value,
                "f1_score": round(f1, 4)
            }

        label_accuracy = label_correct / len(fields)
        entity_f1 = total_f1 / len(fields)

        return jsonify({
            "status": "success",
            "mode": "evaluation",
            "predicted": predicted,
            "ground_truth": gt,
            "field_results": field_results,
            "metrics": {
                "label_accuracy": round(label_accuracy, 4),
                "entity_f1": round(entity_f1, 4)
            },
            "raw_text": raw_text
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
