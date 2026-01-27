from app.modules.shop.catalog.routes import bp as shop_catalog_bp
from app.modules.shop.orders.routes import bp as shop_orders_bp
from app.modules.shop.notifications.routes import bp as shop_notifications_bp
from app.modules.shop.public.routes import bp as shop_public_bp
from app.modules.shop.auth.routes import bp as shop_client_auth_bp


def register_shop_modules(app):
    app.register_blueprint(shop_public_bp)
    app.register_blueprint(shop_client_auth_bp)
    app.register_blueprint(shop_catalog_bp)
    app.register_blueprint(shop_orders_bp)
    app.register_blueprint(shop_notifications_bp)
