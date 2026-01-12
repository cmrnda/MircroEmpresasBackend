from flask import Flask
from .extensions import db, migrate, jwt, cors
from .config import Config

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = Config.db_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = Config.jwt_secret()

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    from .db import models

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
