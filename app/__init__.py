from flask import Flask, jsonify
from app.config import Config
from app.extensions import db as sa_db, migrate, cors
from app.security.jwt import init_jwt
from app.common.tenant_context import init_tenant_context

def create_app() -> Flask:
    flask_app = Flask(__name__)

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = Config.db_uri()
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["JWT_SECRET_KEY"] = Config.jwt_secret()

    sa_db.init_app(flask_app)
    migrate.init_app(flask_app, sa_db)
    init_jwt(flask_app)
    cors.init_app(flask_app)

    import app.db.models

    from app.auth.routes import auth_bp
    from app.modules.tenants.routes import tenants_bp
    from app.modules.users.routes import users_bp
    from app.modules.clients.routes import clients_bp

    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(tenants_bp)
    flask_app.register_blueprint(users_bp)
    flask_app.register_blueprint(clients_bp)

    init_tenant_context(flask_app)

    @flask_app.get("/")
    def root():
        return jsonify({"message": "ok"})

    @flask_app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return flask_app
