import secrets
import string
from app.extensions import db
from app.db.models.usuario import Usuario
from app.security.password import hash_password

def _temp_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def platform_reset_usuario_password(usuario_id):
    u = Usuario.query.filter_by(usuario_id=usuario_id).first()
    if not u:
        return None, "not_found"

    temp = _temp_password(10)
    u.password_hash = hash_password(temp)
    db.session.commit()

    return {"ok": True, "usuario_id": int(usuario_id), "temp_password": temp}, None
