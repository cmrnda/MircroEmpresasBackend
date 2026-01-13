from app.extensions import db

class CompraDetalle(db.Model):
    __tablename__ = "compra_detalle"

    compra_detalle_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    compra_id = db.Column(db.BigInteger, nullable=False)
    producto_id = db.Column(db.BigInteger, nullable=False)
    cantidad = db.Column(db.Numeric(12, 3), nullable=False)
    costo_unit = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "compra_detalle_id", name="uq_compra_det_empresa_det_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "compra_id"],
            ["compra.empresa_id", "compra.compra_id"],
            ondelete="CASCADE",
            name="fk_compra_det_compra",
        ),
        db.ForeignKeyConstraint(
            ["empresa_id", "producto_id"],
            ["producto.empresa_id", "producto.producto_id"],
            name="fk_compra_det_producto",
        ),
    )
