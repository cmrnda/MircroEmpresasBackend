from app.extensions import db

class ProductoImagen(db.Model):
    __tablename__ = "producto_imagen"

    image_id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, nullable=False)
    producto_id = db.Column(db.Integer, nullable=False)

    file_path = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    mime_type = db.Column(db.String, nullable=False)
    file_size = db.Column(db.Integer, nullable=False, default=0)
    is_primary = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
