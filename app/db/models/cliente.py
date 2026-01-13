from datetime import datetime
from app.extensions import db

class Cliente(db.Model):
    __tablename__ = "cliente"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "usuario_id", name="uq_cliente_empresa_usuario"),
    )

    cliente_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="SET NULL"))
    nombre_razon = db.Column(db.Text, nullable=False)
    nit_ci = db.Column(db.Text)
    telefono = db.Column(db.Text)
    email = db.Column(db.Text)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    es_generico = db.Column(db.Boolean, nullable=False, default=False)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
