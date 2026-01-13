from app.extensions import db

class SuscripcionPago(db.Model):
    __tablename__ = "suscripcion_pago"

    pago_suscripcion_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    suscripcion_id = db.Column(db.BigInteger, nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    moneda = db.Column(db.Text, nullable=False, server_default="BOB")
    metodo = db.Column(db.Text, nullable=False)
    referencia_qr = db.Column(db.Text, nullable=True)
    estado = db.Column(db.Text, nullable=False)
    pagado_en = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "pago_suscripcion_id", name="uq_suscripcion_pago_empresa_pago_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "suscripcion_id"],
            ["suscripcion.empresa_id", "suscripcion.suscripcion_id"],
            ondelete="CASCADE",
            name="fk_suscripcion_pago_suscripcion",
        ),
    )
