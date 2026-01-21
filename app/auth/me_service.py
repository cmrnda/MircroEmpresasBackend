from app.extensions import db
from app.database.models.usuario import Usuario
from app.security.password import hash_password

def change_my_password(claims: dict, new_password: str):
    t = claims.get("type")
    if t != "user" and t != "platform":
        return False, "forbidden"

    usuario_id = claims.get("usuario_id")
    if not usuario_id:
        return False, "forbidden"

    u = db.session.query(Usuario).filter_by(usuario_id=int(usuario_id)).first()
    if not u:
        return False, "not_found"

    u.password_hash = hash_password(new_password)
    db.session.commit()
    return True, None
