from app.extensions import db

class VentaDetalle(db.Model):
    __tablename__ = "venta_detalle"

    venta_detalle_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    venta_id = db.Column(db.BigInteger, nullable=False)
    producto_id = db.Column(db.BigInteger, nullable=False)
    cantidad = db.Column(db.Numeric(12, 3), nullable=False)
    precio_unit = db.Column(db.Numeric(12, 2), nullable=False)
    descuento = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "venta_detalle_id", name="uq_venta_det_empresa_det_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "venta_id"],
            ["venta.empresa_id", "venta.venta_id"],
            ondelete="CASCADE",
            name="fk_venta_det_venta",
        ),
        db.ForeignKeyConstraint(
            ["empresa_id", "producto_id"],
            ["producto.empresa_id", "producto.producto_id"],
            name="fk_venta_det_producto",
        ),
    )
