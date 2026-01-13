from flask import Flask, g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.extensions import db, migrate, cors
from app.config import Config
from app.security.jwt import init_jwt
from app.auth.routes import auth_bp
from app.system import system_bp

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = Config.db_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = Config.jwt_secret()

    db.init_app(app)
    migrate.init_app(app, db)
    init_jwt(app)
    cors.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(system_bp)

    from app.modules.users import users_bp
    app.register_blueprint(users_bp)

    @app.get("/")
    def root():
        return {"message": "ok"}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.before_request
    def tenant_context():
        if (
            request.path.startswith("/auth/")
            or request.path.startswith("/health")
            or request.path == "/"
            or request.path.startswith("/static/")
        ):
            return

        if request.method == "OPTIONS":
            return

        verify_jwt_in_request()
        claims = get_jwt()
        g.empresa_id = claims.get("empresa_id")
        g.usuario_id = claims.get("usuario_id")
        g.roles = claims.get("roles", [])

    return app
