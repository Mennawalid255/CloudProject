from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
@jwt_required()
def health():
    return jsonify({"status": "ok"})