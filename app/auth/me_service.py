from app.extensions import db
from app.db.models.usuario import Usuario
from app.db.models.cliente import Cliente
from app.security.password import hash_password

def change_my_password(claims, new_password):
    t = claims.get("type")

    if t in ["platform", "user"]:
        usuario_id = claims.get("usuario_id")
        u = Usuario.query.filter_by(usuario_id=usuario_id).first()
        if not u:
            return False, "not_found"
        u.password_hash = hash_password(new_password)
        db.session.commit()
        return True, None

    if t == "client":
        cliente_id = claims.get("cliente_id")
        empresa_id = claims.get("empresa_id")
        c = Cliente.query.filter_by(cliente_id=cliente_id, empresa_id=empresa_id).first()
        if not c:
            return False, "not_found"
        c.password_hash = hash_password(new_password)
        db.session.commit()
        return True, None

    return False, "unsupported_type"
