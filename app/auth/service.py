from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from werkzeug.security import check_password_hash

from app.security.password import verify_password

from app.auth.repository import (
    get_usuario_by_email,
    is_platform_admin,
    touch_usuario_login,
    get_cliente,
    touch_cliente_login,
    list_empresas_for_cliente_email,
    get_tenant_user,
    get_roles_for_user,
    list_empresas_for_usuario,
)
from app.security.password import verify_password
from flask_jwt_extended import create_access_token, create_refresh_token

from app.db.models.token_blocklist import TokenBlocklist
from app.extensions import db


def login_platform(email, password):
    if not email or not password:
        return None

    u = get_usuario_by_email(email)
    if not u or not getattr(u, "activo", False):
        return None

    if not check_password_hash(u.password_hash, password):
        return None

    if not is_platform_admin(u.usuario_id):
        return None

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
    }


def login_client(email, password, empresa_id=None):
    if not email or not password:
        return None

    # Si no viene empresa_id, intentamos resolverla por email
    if not empresa_id:
        empresa_ids = list_empresas_for_cliente_email(email)

        if len(empresa_ids) == 1:
            empresa_id = empresa_ids[0]
        elif len(empresa_ids) > 1:
            return {"error": "empresa_required", "empresas": empresa_ids}
        else:
            return None

    try:
        empresa_id = int(empresa_id)
    except Exception:
        return {"error": "invalid_empresa_id"}

    c = get_cliente(empresa_id, email)
    if not c or not getattr(c, "activo", False):
        return None

    # OJO: verify_password espera (raw, hash)
    if not verify_password(password, c.password_hash):
        return None

    touch_cliente_login(c)

    claims = {
        "type": "client",
        "cliente_id": c.cliente_id,
        "empresa_id": empresa_id,
    }

    access = create_access_token(identity=str(c.cliente_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(c.cliente_id), additional_claims=claims)

    return {
        "access_token": access,
        "refresh_token": refresh,
        "cliente": c.to_dict(),
    }


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

def login_tenant_user(email, password, empresa_id=None):
    if not email or not password:
        return None

    u = get_usuario_by_email(email)
    if not u or not getattr(u, "activo", False):
        return None

    if not verify_password(password, u.password_hash):
        return None

    # ✅ No pedimos empresa_id en login (solo si es ambiguo)
    if not empresa_id:
        empresa_ids = list_empresas_for_usuario(u.usuario_id)
        if len(empresa_ids) == 1:
            empresa_id = empresa_ids[0]
        elif len(empresa_ids) > 1:
            return {"error": "empresa_required", "empresas": empresa_ids}
        else:
            return None

    try:
        empresa_id = int(empresa_id)
    except Exception:
        return {"error": "invalid_empresa_id"}

    ue = get_tenant_user(empresa_id, u.usuario_id)
    if not ue or not getattr(ue, "activo", False):
        return None

    roles = get_roles_for_user(empresa_id, u.usuario_id)

    touch_usuario_login(u)

    claims = {
        "type": "user",
        "usuario_id": u.usuario_id,
        "empresa_id": empresa_id,
        "roles": roles,
    }

    access = create_access_token(identity=str(u.usuario_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(u.usuario_id), additional_claims=claims)

    return {
        "access_token": access,
        "refresh_token": refresh,
        "usuario": u.to_dict(),
        "roles": roles,
    }