from app.extensions import db

class SuscripcionPago(db.Model):
    __tablename__ = "suscripcion_pago"

    pago_suscripcion_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, nullable=False)
    suscripcion_id = db.Column(db.BigInteger, nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    metodo = db.Column(db.Text, nullable=False)
    estado = db.Column(db.Text, nullable=False)
    pagado_en = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def to_dict(self):
        return {
            "pago_suscripcion_id": self.pago_suscripcion_id,
            "empresa_id": self.empresa_id,
            "suscripcion_id": self.suscripcion_id,
            "monto": float(self.monto),
            "metodo": self.metodo,
            "estado": self.estado,
            "pagado_en": self.pagado_en.isoformat(),
        }
