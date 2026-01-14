from app.modules.users.repository import (
    list_users,
    get_user,
    create_user_global,
    attach_user_to_tenant,
    set_roles,
    user_roles,
    update_user,
    detach_user,
)
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from app.db.models.usuario import Usuario
import secrets
import string
from app.extensions import db
from app.modules.users.repository import get_user, user_roles
from app.security.password import hash_password
import secrets
import string
from app.extensions import db
from app.modules.users.repository import get_user, user_roles
from app.security.password import hash_password

def tenant_list_users(empresa_id):
    rows = list_users(empresa_id)
    out = []
    for u, ue in rows:
        out.append({
            **u.to_dict(),
            "tenant_activo": bool(ue.activo),
            "empresa_id": ue.empresa_id,
            "roles": user_roles(empresa_id, u.usuario_id),
        })
    return out

def tenant_create_user(empresa_id, payload):
    email = payload.get("email")
    password = payload.get("password")
    roles = payload.get("roles") or []
    if not email or not password:
        return None, "invalid_payload"

    try:
        u = Usuario.query.filter_by(email=email).first()
        if not u:
            u = create_user_global(email, password)
        attach_user_to_tenant(empresa_id, u.usuario_id)
        set_roles(empresa_id, u.usuario_id, roles)
        db.session.commit()
        return {"usuario": u.to_dict(), "roles": user_roles(empresa_id, u.usuario_id)}, None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_update_user(empresa_id, usuario_id, payload):
    u, ue = get_user(empresa_id, usuario_id)
    if not u:
        return None
    if payload.get("roles") is not None:
        set_roles(empresa_id, usuario_id, payload.get("roles"))
    update_user(u, ue, payload)
    return {
        **u.to_dict(),
        "tenant_activo": bool(ue.activo),
        "empresa_id": empresa_id,
        "roles": user_roles(empresa_id, usuario_id),
    }

def tenant_delete_user(empresa_id, usuario_id):
    u, ue = get_user(empresa_id, usuario_id)
    if not u:
        return False
    detach_user(empresa_id, usuario_id)
    return True

def _temp_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def tenant_reset_usuario_password(empresa_id, usuario_id):
    u, ue = get_user(empresa_id, usuario_id)
    if not u:
        return None, "not_found"

    roles = user_roles(empresa_id, usuario_id)
    if "TENANT_ADMIN" in roles:
        return None, "forbidden_target_role"

    temp = _temp_password(10)
    u.password_hash = hash_password(temp)
    db.session.commit()

    return {"ok": True, "empresa_id": int(empresa_id), "usuario_id": int(usuario_id), "temp_password": temp}, None

def _temp_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def tenant_reset_usuario_password(empresa_id, usuario_id):
    u, ue = get_user(empresa_id, usuario_id)
    if not u:
        return None, "not_found"

    roles = user_roles(empresa_id, usuario_id)
    if "TENANT_ADMIN" in roles:
        return None, "forbidden_target_role"

    temp = _temp_password(10)
    u.password_hash = hash_password(temp)
    db.session.commit()

    return {"ok": True, "empresa_id": int(empresa_id), "usuario_id": int(usuario_id), "temp_password": temp}, None