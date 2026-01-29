import os
from flask import Flask
from flask_cors import CORS

from app.extensions import db, migrate, jwt
from app.modules import register_modules


def create_app():
    app = Flask(__name__)

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")

    if not all([db_host, db_name, db_user, db_pass]):
        raise RuntimeError("Missing DB env vars: DB_HOST/DB_NAME/DB_USER/DB_PASS")

    database_uri = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    app.config.from_mapping(
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=database_uri,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET", "change_me_super_long"),
        JWT_TOKEN_LOCATION=["headers"],
        JWT_HEADER_NAME="Authorization",
        JWT_HEADER_TYPE="Bearer",
    )

    allowed_origins = [
        "https://localhost",
        "http://localhost",
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "capacitor://localhost",
        "ionic://localhost",
    ]

    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
        allow_headers=["Authorization", "Content-Type", "X-Empresa-Id"],
        expose_headers=["Authorization", "X-Empresa-Id"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        max_age=86400,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    register_modules(app)
    return app
