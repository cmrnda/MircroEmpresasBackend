from ...extensions import db

class Plan(db.Model):
    __tablename__ = "plan"

    plan_id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    periodo_cobro = db.Column(db.Text, nullable=False)

class Suscripcion(db.Model):
    __tablename__ = "suscripcion"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "suscripcion_id", name="uq_suscripcion_empresa_id_suscripcion_id"),
    )

    suscripcion_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    plan_id = db.Column(db.BigInteger, db.ForeignKey("plan.plan_id"), nullable=False)
    estado = db.Column(db.Text, nullable=False)
    inicio = db.Column(db.Date, nullable=False)
    fin = db.Column(db.Date)
    renovacion = db.Column(db.Date)

    plan = db.relationship("Plan")
    pagos = db.relationship("SuscripcionPago", back_populates="suscripcion", cascade="all, delete-orphan")

class SuscripcionPago(db.Model):
    __tablename__ = "suscripcion_pago"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "pago_suscripcion_id", name="uq_suscripcion_pago_empresa_id_pago_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "suscripcion_id"],
            ["suscripcion.empresa_id", "suscripcion.suscripcion_id"],
            ondelete="CASCADE",
            name="fk_suscripcion_pago_empresa_suscripcion",
        ),
    )

    pago_suscripcion_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    suscripcion_id = db.Column(db.BigInteger, nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    moneda = db.Column(db.Text, nullable=False, default="BOB")
    metodo = db.Column(db.Text, nullable=False)
    referencia_qr = db.Column(db.Text)
    estado = db.Column(db.Text, nullable=False)
    pagado_en = db.Column(db.DateTime(timezone=True))

    suscripcion = db.relationship("Suscripcion", back_populates="pagos")
