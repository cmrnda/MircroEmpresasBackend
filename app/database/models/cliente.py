from app.extensions import db


class Cliente(db.Model):
    __tablename__ = "cliente"

    cliente_id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    nombre_razon = db.Column(db.Text, nullable=False)
    nit_ci = db.Column(db.Text)
    telefono = db.Column(db.Text)
    activo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    ultimo_login = db.Column(db.DateTime(timezone=True))

    empresas = db.relationship("ClienteEmpresa", back_populates="cliente", cascade="all, delete-orphan")
    notificaciones = db.relationship("Notificacion", back_populates="cliente")

    def to_dict(self):
        return {
            "cliente_id": int(self.cliente_id),
            "email": self.email,
            "nombre_razon": self.nombre_razon,
            "nit_ci": self.nit_ci,
            "telefono": self.telefono,
            "activo": bool(self.activo),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "ultimo_login": self.ultimo_login.isoformat() if self.ultimo_login else None,
        }


class ClienteEmpresa(db.Model):
    __tablename__ = "cliente_empresa"

    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), primary_key=True)
    cliente_id = db.Column(db.BigInteger, db.ForeignKey("cliente.cliente_id", ondelete="CASCADE"), primary_key=True)

    activo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

    empresa = db.relationship("Empresa", back_populates="clientes_empresa")
    cliente = db.relationship("Cliente", back_populates="empresas")

    def to_dict(self):
        return {
            "empresa_id": int(self.empresa_id),
            "cliente_id": int(self.cliente_id),
            "activo": bool(self.activo),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }
