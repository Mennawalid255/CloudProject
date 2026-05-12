import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

DB_PATH = os.path.join(INSTANCE_DIR, "users.db")

def get_database_uri():
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME", "invoices_db")
    db_user = os.environ.get("DB_USER", "admin")
    db_password = os.environ.get("DB_PASSWORD", "")
    if db_host:
        return f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    return f"sqlite:///{DB_PATH}"

class Config:
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    SQLALCHEMY_DATABASE_URI = get_database_uri()
