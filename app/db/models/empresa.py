from datetime import datetime
from app.extensions import db

class Empresa(db.Model):
    __tablename__ = "empresa"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.Text, nullable=False)
    nit = db.Column(db.Text)
    estado = db.Column(db.Text, nullable=False, default="ACTIVA")
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

class EmpresaConfig(db.Model):
    __tablename__ = "empresa_config"

    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), primary_key=True)
    moneda = db.Column(db.Text, nullable=False, default="BOB")
    tasa_impuesto = db.Column(db.Numeric(6, 3), nullable=False, default=0)
    logo_url = db.Column(db.Text)
    actualizado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
