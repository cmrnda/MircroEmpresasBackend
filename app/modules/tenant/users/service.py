from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.tenant.users.repository import (
    list_users,
    get_usuario,
    get_membership,
    get_roles,
    create_user,
    add_membership,
    set_membership_active,
    set_roles,
    set_password,
)

def tenant_list_users(empresa_id: int, q=None, include_inactivos=False):
    rows = list_users(empresa_id, q=q, include_inactivos=include_inactivos)
    out = []
    for u, m in rows:
        d = u.to_dict()
        d["empresa_id"] = int(m.empresa_id)
        d["membership_activo"] = bool(m.activo)
        d["roles"] = get_roles(empresa_id, u.usuario_id)
        out.append(d)
    return out

def tenant_get_user(empresa_id: int, usuario_id: int, include_inactivos=False):
    m = get_membership(empresa_id, usuario_id)
    if not m:
        return None
    if not include_inactivos and not bool(m.activo):
        return None

    u = get_usuario(usuario_id)
    if not u:
        return None
    if not include_inactivos and not bool(u.activo):
        return None

    d = u.to_dict()
    d["empresa_id"] = int(empresa_id)
    d["membership_activo"] = bool(m.activo)
    d["roles"] = get_roles(empresa_id, usuario_id)
    return d

def tenant_create_user(empresa_id: int, payload: dict):
    email = (payload.get("email") or "").strip()
    password = payload.get("password")
    roles = payload.get("roles") or []

    if not email or not password:
        return None, "invalid_payload"

    try:
        u = create_user(email, password)
        add_membership(empresa_id, u.usuario_id)
        set_roles(empresa_id, u.usuario_id, roles)
        db.session.commit()
        return tenant_get_user(empresa_id, u.usuario_id, include_inactivos=True), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_update_user(empresa_id: int, usuario_id: int, payload: dict):
    m = get_membership(empresa_id, usuario_id)
    if not m:
        return None, "not_found"

    u = get_usuario(usuario_id)
    if not u:
        return None, "not_found"

    roles = payload.get("roles")
    new_password = payload.get("new_password")
    membership_activo = payload.get("membership_activo")
    usuario_activo = payload.get("usuario_activo")

    try:
        if membership_activo is not None:
            set_membership_active(m, bool(membership_activo))

        if usuario_activo is not None:
            u.activo = bool(usuario_activo)
            db.session.add(u)

        if roles is not None:
            set_roles(empresa_id, usuario_id, roles)

        if new_password is not None and str(new_password).strip() != "":
            set_password(u, str(new_password))

        db.session.commit()
        return tenant_get_user(empresa_id, usuario_id, include_inactivos=True), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_disable_membership(empresa_id: int, usuario_id: int):
    m = get_membership(empresa_id, usuario_id)
    if not m:
        return False

    set_membership_active(m, False)
    db.session.commit()
    return True

def tenant_restore_membership(empresa_id: int, usuario_id: int):
    add_membership(empresa_id, usuario_id)
    db.session.commit()
    return tenant_get_user(empresa_id, usuario_id, include_inactivos=True)
