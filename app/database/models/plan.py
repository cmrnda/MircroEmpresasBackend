from app.extensions import db


class Plan(db.Model):
    __tablename__ = "plan"

    plan_id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    periodo_cobro = db.Column(db.Text, nullable=False)

    empresas_settings = db.relationship("EmpresaSettings", back_populates="plan")

    def to_dict(self):
        return {
            "plan_id": int(self.plan_id),
            "nombre": self.nombre,
            "precio": float(self.precio) if self.precio is not None else 0.0,
            "periodo_cobro": self.periodo_cobro,
        }
