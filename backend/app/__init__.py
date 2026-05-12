from flask import Flask 
from flask_cors import CORS

from app.config import Config
from app.extensions import db, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    print("DB PATH:", app.config["SQLALCHEMY_DATABASE_URI"])

    CORS(app, 
     resources={r"/*": {"origins": "*"}},
     supports_credentials=False,
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
     expose_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    db.init_app(app)
    jwt.init_app(app)
    from app.routes.auth import auth_bp
    from app.routes.upload import upload_bp
    from app.routes.extract import extract_bp
    from app.routes.health import health_bp
    from app.routes.evaluate import evaluate_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp, url_prefix="/upload")
    app.register_blueprint(extract_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(evaluate_bp)
    with app.app_context():
        db.create_all()
    return app
