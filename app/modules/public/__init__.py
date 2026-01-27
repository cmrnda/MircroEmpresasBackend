from app.modules.public.brand import bp as public_brand_bp


def register_public_modules(app):
    app.register_blueprint(public_brand_bp)
