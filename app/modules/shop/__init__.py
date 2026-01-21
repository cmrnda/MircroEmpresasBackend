from app.modules.shop.catalog.routes import bp as shop_catalog_bp
from app.modules.shop.orders.routes import bp as shop_orders_bp

def register_shop_modules(app):
    app.register_blueprint(shop_catalog_bp)
    app.register_blueprint(shop_orders_bp)
