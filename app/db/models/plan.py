from app.extensions import db


class Plan(db.Model):
    __tablename__ = "plan"

    plan_id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Numeric(12, 2), nullable=False)
    periodo_cobro = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "plan_id": self.plan_id,
            "nombre": self.nombre,
            "precio": float(self.precio),
            "periodo_cobro": self.periodo_cobro,
        }
