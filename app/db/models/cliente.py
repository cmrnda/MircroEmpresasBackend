from app.extensions import db

class Cliente(db.Model):
    __tablename__ = "cliente"

    cliente_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    email = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    nombre_razon = db.Column(db.Text, nullable=False)
    nit_ci = db.Column(db.Text, nullable=True)
    telefono = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, nullable=False, server_default="true")
    creado_en = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    ultimo_login = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "cliente_id", name="uq_cliente_empresa_cliente_id"),
        db.UniqueConstraint("empresa_id", "email", name="uq_cliente_empresa_email"),
    )

    def to_dict(self):
        return {
            "cliente_id": self.cliente_id,
            "empresa_id": self.empresa_id,
            "email": self.email,
            "nombre_razon": self.nombre_razon,
            "nit_ci": self.nit_ci,
            "telefono": self.telefono,
            "activo": bool(self.activo),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "ultimo_login": self.ultimo_login.isoformat() if self.ultimo_login else None,
        }
