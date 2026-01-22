from app.modules.auth.routes import bp as auth_bp

from app.modules.platform.tenants.routes import bp as platform_tenants_bp
from app.modules.platform.plans.routes import bp as platform_plans_bp
from app.modules.platform.subscriptions import bp as platform_subscriptions_bp
from app.modules.platform.clients.routes import bp as platform_clients_bp
from app.modules.platform.users.routes import bp as platform_users_bp

from app.modules.shop.catalog.routes import bp as shop_catalog_bp
from app.modules.shop.orders.routes import bp as shop_orders_bp

from app.modules.tenant.categories.routes import bp as tenant_categories_bp
from app.modules.tenant.clients.routes import bp as tenant_clients_bp
from app.modules.tenant.orders.routes import bp as tenant_orders_bp
from app.modules.tenant.products.routes import bp as tenant_products_bp
from app.modules.tenant.users.routes import bp as tenant_users_bp
from app.modules.tenant.settings.routes import bp as tenant_settings_bp
from app.modules.tenant.suppliers.routes import bp as tenant_suppliers_bp
from app.modules.tenant.finance.routes import bp as tenant_finances_bp
from app.modules.tenant.purchases.routes import bp as tenant_purchases_bp

def register_modules(app):
    # auth
    app.register_blueprint(auth_bp)

    # platform
    app.register_blueprint(platform_tenants_bp)
    app.register_blueprint(platform_plans_bp)
    app.register_blueprint(platform_subscriptions_bp)
    app.register_blueprint(platform_clients_bp)
    app.register_blueprint(platform_users_bp)

    # tenant
    app.register_blueprint(tenant_categories_bp)
    app.register_blueprint(tenant_products_bp)
    app.register_blueprint(tenant_clients_bp)
    app.register_blueprint(tenant_users_bp)
    app.register_blueprint(tenant_orders_bp)
    app.register_blueprint(tenant_settings_bp)
    app.register_blueprint(tenant_suppliers_bp)
    app.register_blueprint(tenant_finances_bp)
    app.register_blueprint(tenant_purchases_bp)

    # shop
    app.register_blueprint(shop_catalog_bp)
    app.register_blueprint(shop_orders_bp)
