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

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "suscripcion_id", name="uq_suscripcion_empresa_suscripcion_id"),
    )
