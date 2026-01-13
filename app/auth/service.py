from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from werkzeug.security import check_password_hash

from app.auth.repository import (
    get_usuario_by_email,
    is_platform_admin,
    get_tenant_user,
    get_roles_for_user,
    touch_usuario_login,
    get_cliente,
    touch_cliente_login,
)
from app.db.models.token_blocklist import TokenBlocklist
from app.extensions import db


def login_platform(email, password):
    u = get_usuario_by_email(email)
    if not u or not u.activo:
        return None
    if not check_password_hash(u.password_hash, password):
        return None
    if not is_platform_admin(u.usuario_id):
        return None
    touch_usuario_login(u)
    claims = {"type": "platform", "usuario_id": u.usuario_id, "roles": ["PLATFORM_ADMIN"]}
    access = create_access_token(identity=str(u.usuario_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(u.usuario_id), additional_claims=claims)
    return {"access_token": access, "refresh_token": refresh, "usuario": u.to_dict()}


def login_tenant_user(email, password, empresa_id):
    u = get_usuario_by_email(email)
    if not u or not u.activo:
        return None
    if not check_password_hash(u.password_hash, password):
        return None
    ue = get_tenant_user(empresa_id, u.usuario_id)
    if not ue or not ue.activo:
        return None
    roles = get_roles_for_user(empresa_id, u.usuario_id)
    touch_usuario_login(u)
    claims = {"type": "user", "usuario_id": u.usuario_id, "empresa_id": int(empresa_id), "roles": roles}
    access = create_access_token(identity=str(u.usuario_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(u.usuario_id), additional_claims=claims)
    return {"access_token": access, "refresh_token": refresh, "usuario": u.to_dict(), "roles": roles}


def login_client(email, password, empresa_id):
    c = get_cliente(empresa_id, email)
    if not c or not c.activo:
        return None
    if not check_password_hash(c.password_hash, password):
        return None
    touch_cliente_login(c)
    claims = {"type": "client", "cliente_id": c.cliente_id, "empresa_id": int(empresa_id)}
    access = create_access_token(identity=str(c.cliente_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(c.cliente_id), additional_claims=claims)
    return {"access_token": access, "refresh_token": refresh, "cliente": c.to_dict()}


def logout_current_token():
    claims = get_jwt()
    jti = claims.get("jti")
    usuario_id = claims.get("usuario_id")
    if not jti:
        return False
    row = TokenBlocklist(jti=jti, usuario_id=usuario_id)
    db.session.add(row)
    db.session.commit()
    return True
