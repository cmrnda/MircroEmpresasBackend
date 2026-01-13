from flask import Flask, g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.extensions import db, migrate
from app.security.jwt import init_jwt
from app.auth.routes import auth_bp

from app.system import system_bp  # 👈 nuevo
import app.system.routes  # 👈 asegura que carguen las rutas

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    init_jwt(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(system_bp)  # 👈 nuevo

    @app.before_request
    def tenant_context():
        # Permitir endpoints públicos y archivos estáticos
        if (
            request.path.startswith("/auth/")
            or request.path.startswith("/health")
            or request.path.startswith("/static/")
        ):
            return

        # Opcional: deja pasar preflight CORS sin JWT
        if request.method == "OPTIONS":
            return

        verify_jwt_in_request()
        claims = get_jwt()
        g.empresa_id = claims.get("empresa_id")
        g.usuario_id = claims.get("usuario_id")
        g.roles = claims.get("roles", [])

    return app
