from app.extensions import db


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
        db.UniqueConstraint("empresa_id", "codigo", name="uq_producto_empresa_codigo"),
        db.UniqueConstraint("empresa_id", "producto_id", name="uq_producto_empresa_producto_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "categoria_id"],
            ["categoria.empresa_id", "categoria.categoria_id"],
        ),
        db.CheckConstraint("precio >= 0", name="ck_producto_precio"),
        db.CheckConstraint("stock >= 0", name="ck_producto_stock"),
        db.CheckConstraint("stock_min >= 0", name="ck_producto_stock_min"),
        db.Index("idx_producto_empresa", "empresa_id"),
        db.Index("idx_producto_categoria", "empresa_id", "categoria_id"),
    )

    empresa = db.relationship("Empresa", back_populates="productos", overlaps="productos")

    categoria = db.relationship(
        "Categoria",
        back_populates="productos",
        primaryjoin="and_(Producto.empresa_id==Categoria.empresa_id, Producto.categoria_id==Categoria.categoria_id)",
        foreign_keys="[Producto.empresa_id, Producto.categoria_id]",
        overlaps="empresa,productos",
    )

    imagen = db.relationship("ProductoImagen", uselist=False, back_populates="producto", cascade="all, delete-orphan")

    detalles_venta = db.relationship("VentaDetalle", back_populates="producto")

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
