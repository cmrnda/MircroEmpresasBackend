from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
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
from app.extensions import db
from app.db.models.token_blocklist import TokenBlocklist

def login_platform(email, password):
    u = get_usuario_by_email(email)
    if not u or not u.activo:
        return None, "invalid_credentials"
    if not check_password_hash(u.password_hash, password):
        return None, "invalid_credentials"
    if not is_platform_admin(u.usuario_id):
        return None, "invalid_credentials"
    touch_usuario_login(u)
    claims = {"type": "platform", "usuario_id": u.usuario_id, "roles": ["PLATFORM_ADMIN"]}
    access = create_access_token(identity=str(u.usuario_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(u.usuario_id), additional_claims=claims)
    return {"access_token": access, "refresh_token": refresh, "usuario": u.to_dict()}, None

def login_tenant_user(email, password, empresa_id_header):
    u = get_usuario_by_email(email)
    if not u or not u.activo:
        return None, "invalid_credentials"
    if not check_password_hash(u.password_hash, password):
        return None, "invalid_credentials"

    memberships = tenant_memberships(u.usuario_id)
    if len(memberships) == 0:
        return None, "invalid_credentials"

    empresa_id = None
    if empresa_id_header:
        try:
            empresa_id = int(empresa_id_header)
        except Exception:
            return None, "invalid_empresa_header"
        if not any(m["empresa_id"] == empresa_id for m in memberships):
            return None, "forbidden_empresa"
    else:
        if len(memberships) == 1:
            empresa_id = memberships[0]["empresa_id"]
        else:
            return {"tenants": memberships}, "empresa_required"

    ue = get_tenant_user(empresa_id, u.usuario_id)
    if not ue or not ue.activo:
        return None, "invalid_credentials"

    roles = get_roles_for_user(empresa_id, u.usuario_id)
    touch_usuario_login(u)

    claims = {"type": "user", "usuario_id": u.usuario_id, "empresa_id": int(empresa_id), "roles": roles}
    access = create_access_token(identity=str(u.usuario_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(u.usuario_id), additional_claims=claims)

    return {"access_token": access, "refresh_token": refresh, "usuario": u.to_dict(), "roles": roles, "empresa_id": int(empresa_id)}, None

def login_client(email, password, empresa_id_header):
    empresa_id = None
    if empresa_id_header:
        try:
            empresa_id = int(empresa_id_header)
        except Exception:
            return None, "invalid_empresa_header"
        c = get_cliente(empresa_id, email)
        if not c or not c.activo:
            return None, "invalid_credentials"
    else:
        matches = clients_by_email(email)
        if len(matches) == 0:
            return None, "invalid_credentials"
        if len(matches) > 1:
            return {"tenants": matches}, "empresa_required"
        empresa_id = matches[0]["empresa_id"]
        c = get_cliente(empresa_id, email)
        if not c or not c.activo:
            return None, "invalid_credentials"

    if not check_password_hash(c.password_hash, password):
        return None, "invalid_credentials"

    touch_cliente_login(c)
    claims = {"type": "client", "cliente_id": c.cliente_id, "empresa_id": int(empresa_id)}
    access = create_access_token(identity=str(c.cliente_id), additional_claims=claims)
    refresh = create_refresh_token(identity=str(c.cliente_id), additional_claims=claims)
    return {"access_token": access, "refresh_token": refresh, "cliente": c.to_dict(), "empresa_id": int(empresa_id)}, None

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
