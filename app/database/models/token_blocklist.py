from app.extensions import db


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    jti = db.Column(db.Text, primary_key=True)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="SET NULL"))
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

    __table_args__ = (
        db.Index("idx_token_blocklist_usuario", "usuario_id"),
    )

    usuario = db.relationship("Usuario", back_populates="token_blocklist")

    def to_dict(self):
        return {
            "jti": self.jti,
            "usuario_id": int(self.usuario_id) if self.usuario_id is not None else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }
