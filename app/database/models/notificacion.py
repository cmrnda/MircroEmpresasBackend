from app.extensions import db


class Notificacion(db.Model):
    __tablename__ = "notificacion"

    notificacion_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)

    actor_type = db.Column(db.Text, nullable=False)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="CASCADE"))
    cliente_id = db.Column(db.BigInteger, db.ForeignKey("cliente.cliente_id", ondelete="CASCADE"))

    canal = db.Column(db.Text, nullable=False)
    titulo = db.Column(db.Text, nullable=False)
    cuerpo = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    leido_en = db.Column(db.DateTime(timezone=True))

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "notificacion_id", name="uq_notificacion_empresa_notificacion_id"),
        db.CheckConstraint(
            "((actor_type = 'user' and usuario_id is not null and cliente_id is null) or (actor_type = 'client' and cliente_id is not null and usuario_id is null))",
            name="ck_notificacion_actor",
        ),
        db.Index("idx_notificacion_empresa", "empresa_id"),
    )

    empresa = db.relationship("Empresa", back_populates="notificaciones")
    usuario = db.relationship("Usuario", back_populates="notificaciones")
    cliente = db.relationship("Cliente", back_populates="notificaciones")

    def to_dict(self):
        return {
            "notificacion_id": int(self.notificacion_id),
            "empresa_id": int(self.empresa_id),
            "actor_type": self.actor_type,
            "usuario_id": int(self.usuario_id) if self.usuario_id is not None else None,
            "cliente_id": int(self.cliente_id) if self.cliente_id is not None else None,
            "canal": self.canal,
            "titulo": self.titulo,
            "cuerpo": self.cuerpo,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "leido_en": self.leido_en.isoformat() if self.leido_en else None,
        }
