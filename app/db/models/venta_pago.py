from app.extensions import db

class VentaPago(db.Model):
    __tablename__ = "venta_pago"

    venta_pago_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    venta_id = db.Column(db.BigInteger, nullable=False)
    metodo = db.Column(db.Text, nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    referencia_qr = db.Column(db.Text, nullable=True)
    estado = db.Column(db.Text, nullable=False)
    pagado_en = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "venta_pago_id", name="uq_venta_pago_empresa_pago_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "venta_id"],
            ["venta.empresa_id", "venta.venta_id"],
            ondelete="CASCADE",
            name="fk_venta_pago_venta",
        ),
    )
