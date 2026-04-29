import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


# -----------------------
# REGISTER
# -----------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    print("ABSOLUTE DB FILE CHECK:")
    print(os.path.abspath("instance/users.db"))
    print("FILE EXISTS:", os.path.exists("instance/users.db"))
    print("DB ENGINE:", db.engine.url)

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    # check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 409

    hashed_password = generate_password_hash(password)

    user = User(email=email, password=hashed_password)

    try:
        db.session.add(user)
        db.session.commit()

        print("REGISTER SUCCESS - USER SAVED")

        print("ALL USERS:", User.query.all())

    except Exception as e:
        db.session.rollback()
        print("REGISTER ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Registered successfully"}), 201


# -----------------------
# LOGIN
# -----------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    print("ABSOLUTE DB FILE CHECK:")
    print(os.path.abspath("instance/users.db"))
    print("FILE EXISTS:", os.path.exists("instance/users.db"))
    print("DB ENGINE:", db.engine.url)

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    print("USER FOUND:", user)
    print("ALL USERS:", User.query.all())

    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity=user.email)

    return jsonify({
        "access_token": token,
        "email": user.email
    }), 200