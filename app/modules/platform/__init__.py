from app.modules.platform.tenants.routes import bp as platform_tenants_bp
from app.modules.platform.plans.routes import bp as platform_plans_bp
from app.modules.platform.subscriptions.routes import bp as platform_subscriptions_bp
from app.modules.platform.clients.routes import bp as platform_clients_bp
from app.modules.platform.users.routes import bp as platform_users_bp

def register_platform_modules(app):
    app.register_blueprint(platform_tenants_bp)
    app.register_blueprint(platform_plans_bp)
    app.register_blueprint(platform_subscriptions_bp)
    app.register_blueprint(platform_clients_bp)
    app.register_blueprint(platform_users_bp)
