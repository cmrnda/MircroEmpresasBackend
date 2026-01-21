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

    database_uri = (
        f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        "?sslmode=require"
    )

    app.config.from_mapping(
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=database_uri,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET", "change_me_super_long"),
        JWT_TOKEN_LOCATION=["headers"],
        JWT_HEADER_NAME="Authorization",
        JWT_HEADER_TYPE="Bearer",
    )

    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True,
        expose_headers=["Authorization", "X-Empresa-Id"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Empresa-Id",
        ],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    register_modules(app)

    return app