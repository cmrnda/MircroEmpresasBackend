from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.security.password import verify_password
from app.modules.auth.repository import (
    get_usuario_by_email,
    get_cliente_by_email,
    is_platform_admin,
    get_empresa,
    get_membership,
    get_tenant_roles,
    get_cliente_empresa_link,
    touch_usuario_login,
    touch_cliente_login,
    revoke_jti,
)

def platform_login(email: str, password: str):
    u = get_usuario_by_email(email)
    if not u or not bool(u.activo):
        return None, "invalid_credentials"
    if not verify_password(password, u.password_hash):
        return None, "invalid_credentials"
    if not is_platform_admin(u.usuario_id):
        return None, "forbidden"

    claims = {
        "actor_type": "user",
        "usuario_id": int(u.usuario_id),
        "empresa_id": None,
        "cliente_id": None,
        "roles": ["PLATFORM_ADMIN"],
    }

    with db.session.begin():
        touch_usuario_login(u)

    token = create_access_token(identity=str(u.usuario_id), additional_claims=claims)
    return {"access_token": token, "user": u.to_dict(), "claims": claims}, None

def tenant_login(empresa_id: int, email: str, password: str):
    e = get_empresa(empresa_id)
    if not e or e.estado != "ACTIVA":
        return None, "invalid_tenant"
    u = get_usuario_by_email(email)
    if not u or not bool(u.activo):
        return None, "invalid_credentials"
    if not verify_password(password, u.password_hash):
        return None, "invalid_credentials"

    m = get_membership(empresa_id, u.usuario_id)
    if not m or not bool(m.activo):
        return None, "forbidden"

    roles = get_tenant_roles(empresa_id, u.usuario_id)
    if len(roles) == 0:
        return None, "forbidden"

    claims = {
        "actor_type": "user",
        "usuario_id": int(u.usuario_id),
        "empresa_id": int(empresa_id),
        "cliente_id": None,
        "roles": roles,
    }

    with db.session.begin():
        touch_usuario_login(u)

    token = create_access_token(identity=f"{empresa_id}:{u.usuario_id}", additional_claims=claims)
    return {"access_token": token, "user": u.to_dict(), "empresa": e.to_dict(), "claims": claims}, None

def client_login(empresa_id: int, email: str, password: str):
    e = get_empresa(empresa_id)
    if not e or e.estado != "ACTIVA":
        return None, "invalid_tenant"
    c = get_cliente_by_email(email)
    if not c or not bool(c.activo):
        return None, "invalid_credentials"
    if not verify_password(password, c.password_hash):
        return None, "invalid_credentials"

    link = get_cliente_empresa_link(empresa_id, c.cliente_id)
    if not link or not bool(link.activo):
        return None, "forbidden"

    claims = {
        "actor_type": "client",
        "usuario_id": None,
        "empresa_id": int(empresa_id),
        "cliente_id": int(c.cliente_id),
        "roles": ["CLIENT"],
    }

    with db.session.begin():
        touch_cliente_login(c)

    token = create_access_token(identity=f"{empresa_id}:{c.cliente_id}", additional_claims=claims)
    return {"access_token": token, "client": c.to_dict(), "empresa": e.to_dict(), "claims": claims}, None

def logout(jti: str, usuario_id: int | None):
    try:
        with db.session.begin():
            revoke_jti(jti, usuario_id)
        return True
    except IntegrityError:
        db.session.rollback()
        return False
