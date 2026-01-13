from app.extensions import db

class Notificacion(db.Model):
    __tablename__ = "notificacion"

    notificacion_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="CASCADE"), nullable=False)
    canal = db.Column(db.Text, nullable=False)
    titulo = db.Column(db.Text, nullable=False)
    cuerpo = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    leido_en = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "notificacion_id", name="uq_notif_empresa_notif_id"),
    )
