import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

DB_PATH = os.path.join(INSTANCE_DIR, "users.db")

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

    # Use MySQL if DB_HOST is set, otherwise fall back to SQLite
    DB_HOST = os.environ.get("DB_HOST")
    DB_NAME = os.environ.get("DB_NAME", "invoices_db")
    DB_USER = os.environ.get("DB_USER", "admin")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

    if DB_HOST:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
        