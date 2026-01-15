from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from werkzeug.security import check_password_hash

try:
    from app.security.password import verify_password as _verify_password
except Exception:
    _verify_password = None

from app.auth.repository import (
    get_usuario_by_email,
    is_platform_admin,
    tenant_memberships,
    get_tenant_user,
    get_roles_for_user,
    touch_usuario_login,
    clients_by_email,
    get_cliente,
    touch_cliente_login,
)

from app.db.models.token_blocklist import TokenBlocklist
from app.extensions import db


def _pwd_ok(raw_password, hashed_password):
    if _verify_password:
        return bool(_verify_password(raw_password, hashed_password))
    return bool(check_password_hash(hashed_password, raw_password))


def _to_int(value):
    if value is None or value == "":
        return None, None
    try:
        return int(value), None
    except Exception:
        return None, "invalid_empresa_id"


def login_platform(email, password):
    if not email or not password:
        return None, "invalid_payload"

    u = get_usuario_by_email(email)
    if not u or not getattr(u, "activo", False):
        return None, "invalid_credentials"

    if not _pwd_ok(password, u.password_hash):
        return None, "invalid_credentials"

    if not is_platform_admin(u.usuario_id):
        return None, "invalid_credentials"

    touch_usuario_login(u)

    claims = {
        "type": "platform",
        "usuario_id": u.usuario_id,
        "roles": ["PLATFORM_ADMIN"],
    }

    access = create_access_token(identity=str(u.usuario_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(u.usuario_id), additional_claims=claims)

    return {
        "access_token": access,
        "refresh_token": refresh,
        "usuario": u.to_dict(),
    }, None


def login_tenant_user(email, password, empresa_id=None):
    if not email or not password:
        return None, "invalid_payload"

    u = get_usuario_by_email(email)
    if not u or not getattr(u, "activo", False):
        return None, "invalid_credentials"

    if not _pwd_ok(password, u.password_hash):
        return None, "invalid_credentials"

    memberships = tenant_memberships(u.usuario_id) or []
    if len(memberships) == 0:
        return None, "invalid_credentials"

    empresa_id_int, err = _to_int(empresa_id)
    if err:
        return None, err

    if empresa_id_int is None:
        if len(memberships) == 1:
            empresa_id_int = int(memberships[0]["empresa_id"])
        else:
            return {"tenants": memberships}, "empresa_required"
    else:
        if not any(int(m.get("empresa_id")) == empresa_id_int for m in memberships):
            return None, "forbidden_empresa"

    ue = get_tenant_user(empresa_id_int, u.usuario_id)
    if not ue or not getattr(ue, "activo", False):
        return None, "invalid_credentials"

    roles = get_roles_for_user(empresa_id_int, u.usuario_id) or []
    touch_usuario_login(u)

    claims = {
        "type": "user",
        "usuario_id": u.usuario_id,
        "empresa_id": int(empresa_id_int),
        "roles": roles,
    }

    access = create_access_token(identity=str(u.usuario_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(u.usuario_id), additional_claims=claims)

    return {
        "access_token": access,
        "refresh_token": refresh,
        "usuario": u.to_dict(),
        "roles": roles,
        "empresa_id": int(empresa_id_int),
    }, None


def login_client(email, password, empresa_id=None):
    if not email or not password:
        return None, "invalid_payload"

    empresa_id_int, err = _to_int(empresa_id)
    if err:
        return None, err

    if empresa_id_int is None:
        matches = clients_by_email(email) or []
        if len(matches) == 0:
            return None, "invalid_credentials"
        if len(matches) > 1:
            return {"tenants": matches}, "empresa_required"
        empresa_id_int = int(matches[0]["empresa_id"])

    c = get_cliente(int(empresa_id_int), email)
    if not c or not getattr(c, "activo", False):
        return None, "invalid_credentials"

    if not _pwd_ok(password, c.password_hash):
        return None, "invalid_credentials"

    touch_cliente_login(c)

    claims = {
        "type": "client",
        "cliente_id": c.cliente_id,
        "empresa_id": int(empresa_id_int),
    }

    access = create_access_token(identity=str(c.cliente_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(c.cliente_id), additional_claims=claims)

    return {
        "access_token": access,
        "refresh_token": refresh,
        "cliente": c.to_dict(),
        "empresa_id": int(empresa_id_int),
    }, None


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
