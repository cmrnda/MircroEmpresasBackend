from app.extensions import db

class ProveedorProducto(db.Model):
    __tablename__ = "proveedor_producto"

    empresa_id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    proveedor_id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    producto_id = db.Column(db.BigInteger, nullable=False, primary_key=True)

    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "proveedor_id"],
            ["proveedor.empresa_id", "proveedor.proveedor_id"],
            ondelete="CASCADE",
            name="fk_proveedor_producto_proveedor",
        ),
        db.ForeignKeyConstraint(
            ["empresa_id", "producto_id"],
            ["producto.empresa_id", "producto.producto_id"],
            ondelete="CASCADE",
            name="fk_proveedor_producto_producto",
        ),
        db.Index("ix_pp_empresa_proveedor", "empresa_id", "proveedor_id"),
        db.Index("ix_pp_empresa_producto", "empresa_id", "producto_id"),
    )
