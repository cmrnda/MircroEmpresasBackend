from flask import Flask
from flask_cors import CORS

from app.extensions import init_extensions
from app.security.jwt import init_jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:4200", "http://127.0.0.1:4200"]}},
        allow_headers=["Content-Type", "Authorization", "X-Empresa-Id"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        expose_headers=["Authorization"]
    )

    init_extensions(app)
    init_jwt(app)

    from app.auth.routes import bp as auth_bp
    from app.modules.tenants.routes import bp as tenants_bp
    from app.modules.users.routes import bp as users_bp
    from app.modules.clients.routes import bp as clients_bp
    from app.modules.platform_users.routes import bp as platform_users_bp
    from app.modules.subscriptions.api_platform import bp as platform_subscriptions_bp
    from app.modules.subscriptions.api_tenant import bp as tenant_subscriptions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tenants_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(platform_users_bp)
    app.register_blueprint(platform_subscriptions_bp)
    app.register_blueprint(tenant_subscriptions_bp)

    return app
