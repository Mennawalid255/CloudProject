from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import uuid
import boto3
from botocore.exceptions import ClientError

upload_bp = Blueprint("upload", __name__)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
S3_BUCKET = os.environ.get("S3_BUCKET", "cloudproject-invoices-015518371430")

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_s3(file, filename):
    s3 = boto3.client("s3", region_name="us-east-1")
    try:
        s3.upload_fileobj(file, S3_BUCKET, f"uploads/{filename}")
        return f"https://{S3_BUCKET}.s3.amazonaws.com/uploads/{filename}"
    except ClientError as e:
        print(f"S3 upload error: {e}")
        return None

@upload_bp.route("/", methods=["POST", "OPTIONS"])
def upload_file():

    if request.method == "OPTIONS":
        return "", 200

    from flask_jwt_extended import verify_jwt_in_request
    verify_jwt_in_request()

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

    with open(file_path, "rb") as f:
        s3_url = upload_to_s3(f, unique_name)

    return jsonify({
        "status": "success",
        "message": "File uploaded successfully",
        "file_name": unique_name,
        "uploaded_by": current_user,
        "s3_url": s3_url
    })