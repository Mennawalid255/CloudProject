from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import uuid
from flask import request

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/", methods=["POST"])
@jwt_required()
def upload_file():
   
    current_user = get_jwt_identity()


    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]


    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400


    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

  
    filename = secure_filename(file.filename)

    unique_name = f"{uuid.uuid4()}_{filename}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, unique_name)

    file.save(file_path)

    return jsonify({
        "status": "success",
        "message": "File uploaded successfully",
        "file_name": unique_name,
        "uploaded_by": current_user
    }), 201