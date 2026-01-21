from app.modules.tenant.settings.routes import bp as tenant_settings_bp
from app.modules.tenant.categories.routes import bp as tenant_categories_bp
from app.modules.tenant.products.routes import bp as tenant_products_bp
from app.modules.tenant.product_image.routes import bp as tenant_product_image_bp
from app.modules.tenant.clients.routes import bp as tenant_clients_bp
from app.modules.tenant.users.routes import bp as tenant_users_bp
from app.modules.tenant.orders.routes import bp as tenant_orders_bp
#from app.modules.tenant.notifications.routes import bp as tenant_notifications_bp

def register_tenant_modules(app):
    app.register_blueprint(tenant_settings_bp)
    app.register_blueprint(tenant_categories_bp)
    app.register_blueprint(tenant_products_bp)
    app.register_blueprint(tenant_product_image_bp)
    app.register_blueprint(tenant_clients_bp)
    app.register_blueprint(tenant_users_bp)
    app.register_blueprint(tenant_orders_bp)
#    app.register_blueprint(tenant_notifications_bp)
