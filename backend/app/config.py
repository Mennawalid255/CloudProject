import os
from datetime import timedelta

from sqlalchemy import false

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# instance path
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

# SQLite file directory
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

# path to the database file
DB_PATH = os.path.join(INSTANCE_DIR, "users.db")

class Config:
    DEBUG = True
    SECRET_KEY = "super-secret-key"
    JWT_SECRET_KEY = "jwt-secret-key"

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

JWT_ACCESS_TOKEN_EXPIRES = false

