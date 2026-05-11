from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
import requests
import os

extract_bp = Blueprint("extract", __name__)

MODEL_API_URL = os.environ.get("MODEL_API_URL", "http://localhost:8000")

@extract_bp.route("/extract/<filename>", methods=["GET"])
@jwt_required()
def extract_invoice(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
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
                "message": model_result.get("message", "Model processing failed")
            }), 500

        raw_text = model_result.get("raw_text", "")
        layoutlm_result = model_result.get("layoutlm_extraction")

        
        if layoutlm_result and any(layoutlm_result.values()):
            data = {
                "data": {
                    "company_name": layoutlm_result.get("company_name"),
                    "date": layoutlm_result.get("date"),
                    "total price": layoutlm_result.get("total_price"),
                    "address": layoutlm_result.get("address"),
                    "vat": None,
                    "tax": None,
                    "invoice_number": None
                },
                "errors": [],
                "is_valid": True,
                "source": "layoutlm"
            }
        else:
            from app.services.parser import parse_invoice
            data = parse_invoice(raw_text)
            data["source"] = "regex_parser"

        return jsonify({
            "status": "success",
            "raw_text": raw_text,
            "extracted_data": data,
            "words_and_boxes": model_result.get("words_and_boxes", [])
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
