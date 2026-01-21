from app.extensions import db

class Categoria(db.Model):
    __tablename__ = "categoria"

    categoria_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    nombre = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "nombre"),
        db.UniqueConstraint("empresa_id", "categoria_id"),
    )

    def to_dict(self):
        return {
            "categoria_id": int(self.categoria_id),
            "empresa_id": int(self.empresa_id),
            "nombre": self.nombre,
            "activo": bool(self.activo),
        }

class Producto(db.Model):
    __tablename__ = "producto"

    producto_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    categoria_id = db.Column(db.BigInteger, nullable=False)
    codigo = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    stock = db.Column(db.Numeric(12, 3), nullable=False, server_default="0")
    stock_min = db.Column(db.Integer, nullable=False, server_default="0")
    activo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "codigo"),
        db.UniqueConstraint("empresa_id", "producto_id"),
        db.ForeignKeyConstraint(["empresa_id", "categoria_id"], ["categoria.empresa_id", "categoria.categoria_id"]),
    )

    def to_dict(self):
        return {
            "producto_id": int(self.producto_id),
            "empresa_id": int(self.empresa_id),
            "categoria_id": int(self.categoria_id),
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "precio": float(self.precio) if self.precio is not None else 0.0,
            "stock": float(self.stock) if self.stock is not None else 0.0,
            "stock_min": int(self.stock_min) if self.stock_min is not None else 0,
            "activo": bool(self.activo),
        }

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
    )

    def to_dict(self):
        return {
            "empresa_id": int(self.empresa_id),
            "producto_id": int(self.producto_id),
            "file_path": self.file_path,
            "url": self.url,
            "mime_type": self.mime_type,
            "file_size": int(self.file_size) if self.file_size is not None else 0,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
