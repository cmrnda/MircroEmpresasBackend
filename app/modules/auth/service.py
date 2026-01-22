from datetime import datetime, timezone

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.database.models.usuario import Usuario, UsuarioAdminPlataforma
from app.database.models.token_blocklist import TokenBlocklist
from app.modules.auth.repository import (
    get_usuario_by_email,
    is_platform_admin,
    tenant_memberships,
    get_tenant_user,
    get_roles_for_user,
    clients_by_email,
    get_cliente_by_email,
    get_cliente_for_tenant,
    empresa_activa_exists,
    cliente_link_exists,
    create_cliente,
    create_cliente_link,
)


def signup_platform_admin(email: str, password: str):
    if not email or not password:
        return None, "invalid_payload"

    if get_usuario_by_email(email):
        return None, "email_already_exists"

    u = Usuario(
        email=email,
        password_hash=generate_password_hash(password),
        activo=True,
        creado_en=datetime.now(timezone.utc),
    )
    db.session.add(u)
    db.session.flush()

    db.session.add(UsuarioAdminPlataforma(usuario_id=u.usuario_id))
    db.session.commit()

    return u.to_dict(), None


def _pwd_ok(raw: str, hashed: str) -> bool:
    return check_password_hash(hashed, raw)


def login_platform(email, password):
    u = get_usuario_by_email(email)
    if not u or not u.activo:
        return None, "invalid_credentials"
    if not _pwd_ok(password, u.password_hash):
        return None, "invalid_credentials"
    if not is_platform_admin(u.usuario_id):
        return None, "forbidden"

    u.ultimo_login = datetime.now(timezone.utc)
    db.session.commit()

    claims = {"type": "platform", "usuario_id": u.usuario_id, "roles": ["PLATFORM_ADMIN"]}
    return {
        "access_token": create_access_token(identity=str(u.usuario_id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(u.usuario_id), additional_claims=claims),
        "usuario": u.to_dict(),
    }, None


def login_tenant_user(email, password, empresa_id=None):
    u = get_usuario_by_email(email)
    if not u or not u.activo:
        return None, "invalid_credentials"
    if not _pwd_ok(password, u.password_hash):
        return None, "invalid_credentials"

    memberships = tenant_memberships(u.usuario_id)
    if not memberships:
        return None, "invalid_credentials"

    if empresa_id is None:
        if len(memberships) != 1:
            return {"tenants": memberships}, "empresa_required"
        empresa_id = memberships[0]["empresa_id"]

    ue = get_tenant_user(int(empresa_id), u.usuario_id)
    if not ue or not ue.activo:
        return None, "forbidden"

    roles = get_roles_for_user(int(empresa_id), u.usuario_id)
    if not roles:
        return None, "forbidden"

    u.ultimo_login = datetime.now(timezone.utc)
    db.session.commit()

    claims = {"type": "user", "usuario_id": u.usuario_id, "empresa_id": int(empresa_id), "roles": roles}
    return {
        "access_token": create_access_token(identity=str(u.usuario_id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(u.usuario_id), additional_claims=claims),
        "usuario": u.to_dict(),
        "roles": roles,
        "empresa_id": int(empresa_id),
    }, None


def login_client(email, password, empresa_id=None):
    c = get_cliente_by_email(email)
    if not c or not c.activo:
        return None, "invalid_credentials"
    if not _pwd_ok(password, c.password_hash):
        return None, "invalid_credentials"

    if empresa_id is None:
        matches = clients_by_email(email)
        if len(matches) != 1:
            return {"tenants": matches}, "empresa_required"
        empresa_id = matches[0]["empresa_id"]

    if not get_cliente_for_tenant(int(empresa_id), c.cliente_id):
        return None, "forbidden"

    c.ultimo_login = datetime.now(timezone.utc)
    db.session.commit()

    claims = {"type": "client", "cliente_id": c.cliente_id, "empresa_id": int(empresa_id)}
    return {
        "access_token": create_access_token(identity=str(c.cliente_id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(c.cliente_id), additional_claims=claims),
        "cliente": c.to_dict(),
        "empresa_id": int(empresa_id),
    }, None


def signup_client(email: str, password: str, empresa_id: int, nombre_razon: str = None, telefono: str = None):
    if not email or not password or not empresa_id:
        return None, "invalid_payload"

    if not empresa_activa_exists(int(empresa_id)):
        return None, "empresa_not_found"

    c = get_cliente_by_email(email)

    if c and not c.activo:
        return None, "forbidden"

    if c:
        if cliente_link_exists(int(empresa_id), int(c.cliente_id)):
            return None, "email_already_exists"
    else:
        c = create_cliente(
            email=email,
            password_hash=generate_password_hash(password),
            nombre_razon=nombre_razon,
            telefono=telefono,
        )

    create_cliente_link(int(empresa_id), int(c.cliente_id))

    c.ultimo_login = datetime.now(timezone.utc)
    db.session.commit()

    claims = {"type": "client", "cliente_id": int(c.cliente_id), "empresa_id": int(empresa_id)}
    return {
        "access_token": create_access_token(identity=str(c.cliente_id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(c.cliente_id), additional_claims=claims),
        "cliente": c.to_dict(),
        "empresa_id": int(empresa_id),
    }, None


def logout_current_token():
    jti = (get_jwt() or {}).get("jti")
    usuario_id = (get_jwt() or {}).get("usuario_id")
    if not jti:
        return False
    db.session.add(TokenBlocklist(jti=jti, usuario_id=usuario_id))
    db.session.commit()
    return True
