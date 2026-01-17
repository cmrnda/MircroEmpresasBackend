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
        db.ForeignKeyConstraint(
            ["empresa_id", "suscripcion_id"],
            ["suscripcion.empresa_id", "suscripcion.suscripcion_id"],
            ondelete="CASCADE",
        ),
    )

    def to_dict(self):
        return {
            "pago_suscripcion_id": int(self.pago_suscripcion_id) if self.pago_suscripcion_id is not None else None,
            "empresa_id": int(self.empresa_id) if self.empresa_id is not None else None,
            "suscripcion_id": int(self.suscripcion_id) if self.suscripcion_id is not None else None,
            "monto": float(self.monto) if self.monto is not None else None,
            "moneda": self.moneda,
            "metodo": self.metodo,
            "referencia_qr": self.referencia_qr,
            "estado": self.estado,
            "pagado_en": self.pagado_en.isoformat() if self.pagado_en else None,
        }
