from app.modules.auth.routes import bp as auth_bp
from app.modules.platform.plans.routes import bp as platform_plans_bp
from app.modules.platform.subscriptions.routes import bp as platform_subscriptions_bp
from app.modules.shop.catalog.routes import bp as shop_catalog_bp
from app.modules.shop.orders.routes import bp as shop_orders_bp
from app.modules.tenant.categories.routes import bp as tenant_categories_bp
from app.modules.tenant.clients.routes import bp as tenant_clients_bp
# from app.modules.tenant.notifications.routes import bp as tenant_notifications_bp
from app.modules.tenant.orders.routes import bp as tenant_orders_bp
from app.modules.tenant.product_image.routes import bp as tenant_product_image_bp
from app.modules.tenant.products.routes import bp as tenant_products_bp
from app.modules.tenant.users.routes import bp as tenant_users_bp


def register_modules(app):
    app.register_blueprint(auth_bp)

    app.register_blueprint(platform_plans_bp)
    app.register_blueprint(platform_subscriptions_bp)

    app.register_blueprint(tenant_categories_bp)
    app.register_blueprint(tenant_products_bp)
    app.register_blueprint(tenant_product_image_bp)
    app.register_blueprint(tenant_clients_bp)
    app.register_blueprint(tenant_users_bp)
#    app.register_blueprint(tenant_notifications_bp)
    app.register_blueprint(tenant_orders_bp)

    app.register_blueprint(shop_catalog_bp)
    app.register_blueprint(shop_orders_bp)
