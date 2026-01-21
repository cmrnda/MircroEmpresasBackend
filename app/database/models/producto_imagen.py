from app.extensions import db


class ProductoImagen(db.Model):
    __tablename__ = "producto_imagen"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    producto_id = db.Column(db.BigInteger, primary_key=True)

    file_path = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    mime_type = db.Column(db.Text, nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False, server_default="0")
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "producto_id"],
            ["producto.empresa_id", "producto.producto_id"],
            ondelete="CASCADE",
        ),
        db.CheckConstraint("file_size >= 0", name="ck_producto_imagen_file_size"),
    )

    producto = db.relationship(
        "Producto",
        back_populates="imagen",
        primaryjoin="and_(ProductoImagen.empresa_id==Producto.empresa_id, ProductoImagen.producto_id==Producto.producto_id)",
        foreign_keys="[ProductoImagen.empresa_id, ProductoImagen.producto_id]",
    )

    def to_dict(self):
        return {
            "empresa_id": int(self.empresa_id),
            "producto_id": int(self.producto_id),
            "file_path": self.file_path,
            "url": self.url,
            "mime_type": self.mime_type,
            "file_size": int(self.file_size or 0),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
