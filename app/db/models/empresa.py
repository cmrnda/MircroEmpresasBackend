from app.extensions import db

class Empresa(db.Model):
    __tablename__ = "empresa"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    nit = db.Column(db.Text, nullable=True)
    estado = db.Column(db.Text, nullable=False, server_default="ACTIVA")
    creado_en = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    def to_dict(self):
        return {
            "empresa_id": self.empresa_id,
            "nombre": self.nombre,
            "nit": self.nit,
            "estado": self.estado,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }
