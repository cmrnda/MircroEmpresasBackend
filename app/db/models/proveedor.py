from app.extensions import db

class Proveedor(db.Model):
    __tablename__ = "proveedor"

    proveedor_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    nombre = db.Column(db.Text, nullable=False)
    telefono = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)
    datos_pago = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, nullable=False, server_default="true")

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "proveedor_id", name="uq_proveedor_empresa_proveedor_id"),
    )
