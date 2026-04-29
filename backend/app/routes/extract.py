from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.services.ocr_service import extract_text
from app.services.parser import parse_invoice
import os

extract_bp = Blueprint("extract", __name__)

@extract_bp.route("/extract/<filename>", methods=["GET"])
@jwt_required()
def extract_invoice(filename):

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    print("FILE PATH:", file_path)
    print("EXISTS:", os.path.exists(file_path))

    # 📄 OCR step
    text = extract_text(file_path)
    print("OCR TEXT:", text)

    if not text:
        return jsonify({
            "status": "error",
            "message": "OCR failed or empty text"
        }), 500

    # 🧠 Parsing step
    data = parse_invoice(text)

    return jsonify({
        "status": "success",
        "raw_text": text,
        "extracted_data": data
    }), 200