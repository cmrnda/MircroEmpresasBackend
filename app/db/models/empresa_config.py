from app.extensions import db

class EmpresaConfig(db.Model):
    __tablename__ = "empresa_config"

    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), primary_key=True)
    moneda = db.Column(db.Text, nullable=False, server_default="BOB")
    tasa_impuesto = db.Column(db.Numeric(6, 3), nullable=False, server_default="0")
    logo_url = db.Column(db.Text, nullable=True)
    actualizado_en = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
