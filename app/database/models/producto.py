from app.extensions import db


class Producto(db.Model):
    __tablename__ = "producto"

    producto_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, nullable=False)

    categoria_id = db.Column(db.BigInteger, nullable=False)
    codigo = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

    precio = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    stock = db.Column(db.Numeric(12, 3), nullable=False, server_default="0")
    stock_min = db.Column(db.Integer, nullable=False, server_default="0")
    activo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))

    image_url = db.Column(db.Text, nullable=True)
    empresa = db.relationship("Empresa", back_populates="productos", overlaps="productos")

    categoria = db.relationship(
        "Categoria",
        back_populates="productos",
        primaryjoin="and_(Producto.empresa_id==Categoria.empresa_id, Producto.categoria_id==Categoria.categoria_id)",
        foreign_keys="[Producto.empresa_id, Producto.categoria_id]",
        overlaps="empresa,productos",
    )

    detalles_venta = db.relationship(
        "VentaDetalle",
        back_populates="producto",
        cascade="all, delete-orphan",
        primaryjoin="and_(Producto.empresa_id==VentaDetalle.empresa_id, Producto.producto_id==VentaDetalle.producto_id)",
        foreign_keys="[VentaDetalle.empresa_id, VentaDetalle.producto_id]",
        overlaps="empresa,productos",
    )

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresa.empresa_id"],
            ondelete="CASCADE",
        ),
        db.ForeignKeyConstraint(
            ["empresa_id", "categoria_id"],
            ["categoria.empresa_id", "categoria.categoria_id"],
        ),
        db.UniqueConstraint("empresa_id", "codigo", name="uq_producto_empresa_codigo"),
        db.UniqueConstraint("empresa_id", "producto_id", name="uq_producto_empresa_producto_id"),
        db.CheckConstraint("precio >= 0", name="ck_producto_precio"),
        db.CheckConstraint("stock >= 0", name="ck_producto_stock"),
        db.CheckConstraint("stock_min >= 0", name="ck_producto_stock_min"),
        db.CheckConstraint(
            "image_url is null or image_url ~* '^https?://'",
            name="ck_producto_image_url",
        ),
    )

    def to_dict(self):
        return {
            "producto_id": int(self.producto_id),
            "empresa_id": int(self.empresa_id),
            "categoria_id": int(self.categoria_id),
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "precio": float(self.precio or 0),
            "stock": float(self.stock or 0),
            "stock_min": int(self.stock_min or 0),
            "activo": bool(self.activo),
            "image_url": self.image_url,
           }
