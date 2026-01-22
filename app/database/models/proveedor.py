from app.extensions import db

class Proveedor(db.Model):
    __tablename__ = "proveedor"

    proveedor_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)

    nombre = db.Column(db.Text, nullable=False)
    nit = db.Column(db.Text)
    telefono = db.Column(db.Text)
    direccion = db.Column(db.Text)
    email = db.Column(db.Text)

    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "nombre", name="uq_proveedor_empresa_nombre"),
        db.UniqueConstraint("empresa_id", "proveedor_id", name="uq_proveedor_empresa_id"),
    )

    def to_dict(self):
        return {
            "proveedor_id": int(self.proveedor_id),
            "empresa_id": int(self.empresa_id),
            "nombre": self.nombre,
            "nit": self.nit,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "email": self.email,
            "activo": bool(self.activo),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }
