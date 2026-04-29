import os
from datetime import timedelta

from sqlalchemy import false

# 1. Get the absolute path to the directory containing this file (config.py)
# If config.py is inside an 'app' folder, we go up one level (..) to get to the Root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 2. Define the path for the 'instance' folder at the Root level
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

# 3. Ensure the instance directory actually exists so SQLite can create the file
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

# 4. Create the absolute path to your database file
DB_PATH = os.path.join(INSTANCE_DIR, "users.db")

class Config:
    DEBUG = True
    SECRET_KEY = "super-secret-key"
    JWT_SECRET_KEY = "jwt-secret-key"

    # 5. Tell SQLAlchemy to use the absolute path
    # The 'f' string ensures the sqlite:/// prefix is added correctly
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

JWT_ACCESS_TOKEN_EXPIRES = false

