from app.extensions import db


class Empresa(db.Model):
    __tablename__ = "empresa"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    nit = db.Column(db.Text)
    estado = db.Column(db.Text, nullable=False, server_default="ACTIVA")
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

    settings = db.relationship("EmpresaSettings", uselist=False, back_populates="empresa", cascade="all, delete-orphan")

    categorias = db.relationship("Categoria", back_populates="empresa", cascade="all, delete-orphan")
    productos = db.relationship("Producto", back_populates="empresa", cascade="all, delete-orphan")
    ventas = db.relationship("Venta", back_populates="empresa", cascade="all, delete-orphan")

    usuarios_empresa = db.relationship("UsuarioEmpresa", back_populates="empresa", cascade="all, delete-orphan")
    clientes_empresa = db.relationship("ClienteEmpresa", back_populates="empresa", cascade="all, delete-orphan")

    notificaciones = db.relationship("Notificacion", back_populates="empresa", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "empresa_id": int(self.empresa_id),
            "nombre": self.nombre,
            "nit": self.nit,
            "estado": self.estado,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }
