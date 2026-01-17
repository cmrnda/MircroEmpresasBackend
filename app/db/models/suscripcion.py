from app.extensions import db


class Suscripcion(db.Model):
    __tablename__ = "suscripcion"

    suscripcion_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    plan_id = db.Column(db.BigInteger, db.ForeignKey("plan.plan_id"), nullable=False)

    estado = db.Column(db.Text, nullable=False)
    inicio = db.Column(db.Date, nullable=False)
    fin = db.Column(db.Date, nullable=True)
    renovacion = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            "suscripcion_id": int(self.suscripcion_id) if self.suscripcion_id is not None else None,
            "empresa_id": int(self.empresa_id) if self.empresa_id is not None else None,
            "plan_id": int(self.plan_id) if self.plan_id is not None else None,
            "estado": self.estado,
            "inicio": self.inicio.isoformat() if self.inicio else None,
            "fin": self.fin.isoformat() if self.fin else None,
            "renovacion": self.renovacion.isoformat() if self.renovacion else None,
        }
