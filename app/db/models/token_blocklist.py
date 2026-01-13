from datetime import datetime

from app.extensions import db


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    jti = db.Column(db.Text, primary_key=True)
    usuario_id = db.Column(db.BigInteger, nullable=True)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
