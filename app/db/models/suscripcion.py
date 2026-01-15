from app.extensions import db


class Suscripcion(db.Model):
    __tablename__ = "suscripcion"

    suscripcion_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    plan_id = db.Column(db.BigInteger, db.ForeignKey("plan.plan_id"), nullable=False)
    estado = db.Column(db.Text, nullable=False)
    inicio = db.Column(db.Date, nullable=False)
    fin = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            "suscripcion_id": self.suscripcion_id,
            "empresa_id": self.empresa_id,
            "plan_id": self.plan_id,
            "estado": self.estado,
            "inicio": self.inicio.isoformat(),
            "fin": self.fin.isoformat() if self.fin else None,
        }
