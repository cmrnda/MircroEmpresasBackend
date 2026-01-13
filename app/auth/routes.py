import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.security.password import hash_password, verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _password_ok(pw: str) -> bool:
    if pw is None:
        return False
    b = pw.encode("utf-8")
    return 8 <= len(b) <= 72


def _bootstrap_allowed() -> bool:
    key = (os.getenv("BOOTSTRAP_KEY") or "").strip()
    if not key:
        return True
    req_key = (request.headers.get("X-BOOTSTRAP-KEY") or "").strip()
    return req_key == key


def _update_last_login_usuario(usuario_id: int) -> None:
    db.session.execute(
        text("update usuario set ultimo_login = now() where usuario_id = :u"),
        {"u": usuario_id},
    )
    db.session.commit()


def _update_last_login_cliente(cliente_id: int) -> None:
    db.session.execute(
        text("update cliente set ultimo_login = now() where cliente_id = :c"),
        {"c": cliente_id},
    )
    db.session.commit()


def _is_platform_admin(usuario_id: int) -> bool:
    row = db.session.execute(
        text("select 1 from usuario_admin_plataforma where usuario_id = :u limit 1"),
        {"u": usuario_id},
    ).first()
    return row is not None


def _get_tenant_roles(empresa_id: int, usuario_id: int) -> list:
    roles = []
    r1 = db.session.execute(
        text(
            "select 1 from usuario_admin_empresa where empresa_id=:e and usuario_id=:u limit 1"
        ),
        {"e": empresa_id, "u": usuario_id},
    ).first()
    if r1:
        roles.append("ADMIN_EMPRESA")

    r2 = db.session.execute(
        text(
            "select 1 from usuario_vendedor where empresa_id=:e and usuario_id=:u limit 1"
        ),
        {"e": empresa_id, "u": usuario_id},
    ).first()
    if r2:
        roles.append("VENDEDOR")

    r3 = db.session.execute(
        text(
            "select 1 from usuario_encargado_inventario where empresa_id=:e and usuario_id=:u limit 1"
        ),
        {"e": empresa_id, "u": usuario_id},
    ).first()
    if r3:
        roles.append("ENCARGADO_INVENTARIO")

    return roles


def _primary_role(roles: list) -> str:
    if "ADMIN_PLATAFORMA" in roles:
        return "ADMIN_PLATAFORMA"
    if "ADMIN_EMPRESA" in roles:
        return "ADMIN_EMPRESA"
    if "ENCARGADO_INVENTARIO" in roles:
        return "ENCARGADO_INVENTARIO"
    if "VENDEDOR" in roles:
        return "VENDEDOR"
    if "CLIENTE" in roles:
        return "CLIENTE"
    return "USER"


def _list_tenant_ids_for_user(usuario_id: int) -> list:
    rows = db.session.execute(
        text(
            """
            select empresa_id
            from empresa_usuario
            where usuario_id = :u and activo = true
            order by empresa_id asc
            """
        ),
        {"u": usuario_id},
    ).fetchall()
    return [int(r[0]) for r in rows]


def _issue_platform_token(usuario_id: int) -> str:
    roles = ["ADMIN_PLATAFORMA"]
    claims = {
        "usuario_id": int(usuario_id),
        "roles": roles,
        "primary_role": _primary_role(roles),
        "scope": "PLATFORM",
    }
    return create_access_token(identity=str(usuario_id), additional_claims=claims)


def _issue_tenant_base_token(usuario_id: int, tenant_ids: list) -> str:
    roles = ["TENANT_USER"]
    claims = {
        "usuario_id": int(usuario_id),
        "roles": roles,
        "primary_role": _primary_role(roles),
        "scope": "TENANT_BASE",
        "tenant_ids": tenant_ids,
    }
    return create_access_token(identity=str(usuario_id), additional_claims=claims)


def _issue_tenant_token(usuario_id: int, empresa_id: int, roles: list) -> str:
    claims = {
        "usuario_id": int(usuario_id),
        "empresa_id": int(empresa_id),
        "roles": roles,
        "primary_role": _primary_role(roles),
        "scope": "TENANT",
    }
    return create_access_token(identity=str(usuario_id), additional_claims=claims)


def _issue_client_token(cliente_id: int, empresa_id: int) -> str:
    roles = ["CLIENTE"]
    claims = {
        "cliente_id": int(cliente_id),
        "empresa_id": int(empresa_id),
        "roles": roles,
        "primary_role": _primary_role(roles),
        "scope": "CLIENT",
    }
    return create_access_token(identity=str(cliente_id), additional_claims=claims)


@auth_bp.post("/platform/bootstrap")
def platform_bootstrap():
    if not _bootstrap_allowed():
        return jsonify({"error": "BOOTSTRAP_FORBIDDEN"}), 403

    exists = db.session.execute(
        text("select 1 from usuario_admin_plataforma limit 1")
    ).first()
    if exists:
        return jsonify({"error": "PLATFORM_ADMIN_ALREADY_EXISTS"}), 409

    data = request.get_json() or {}
    email = _normalize_email(data.get("email"))
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "EMAIL_AND_PASSWORD_REQUIRED"}), 400

    if not _password_ok(password):
        return jsonify({"error": "PASSWORD_8_72_BYTES"}), 400

    email_exists = db.session.execute(
        text("select 1 from usuario where email=:email limit 1"),
        {"email": email},
    ).first()
    if email_exists:
        return jsonify({"error": "EMAIL_ALREADY_EXISTS"}), 409

    pw_hash = hash_password(password)

    row = db.session.execute(
        text(
            """
            insert into usuario (email, password_hash, activo, creado_en)
            values (:email, :pw, true, now())
                returning usuario_id
            """
        ),
        {"email": email, "pw": pw_hash},
    ).first()

    usuario_id = int(row[0])

    db.session.execute(
        text("insert into usuario_admin_plataforma (usuario_id) values (:u)"),
        {"u": usuario_id},
    )
    db.session.commit()

    token = _issue_platform_token(usuario_id)

    return (
        jsonify(
            {
                "usuario_id": usuario_id,
                "email": email,
                "roles": ["ADMIN_PLATAFORMA"],
                "primary_role": "ADMIN_PLATAFORMA",
                "access_token": token,
            }
        ),
        201,
    )


@auth_bp.post("/platform/login")
def platform_login():
    data = request.get_json() or {}
    email = _normalize_email(data.get("email"))
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "EMAIL_AND_PASSWORD_REQUIRED"}), 400

    row = db.session.execute(
        text(
            """
            select usuario_id, password_hash, activo
            from usuario
            where email = :email
                limit 1
            """
        ),
        {"email": email},
    ).mappings().first()

    if not row:
        return jsonify({"error": "INVALID_CREDENTIALS"}), 401
    if not row["activo"]:
        return jsonify({"error": "USER_INACTIVE"}), 403
    if not verify_password(password, row["password_hash"]):
        return jsonify({"error": "INVALID_CREDENTIALS"}), 401

    usuario_id = int(row["usuario_id"])
    if not _is_platform_admin(usuario_id):
        return jsonify({"error": "NOT_PLATFORM_ADMIN"}), 403

    _update_last_login_usuario(usuario_id)

    token = _issue_platform_token(usuario_id)

    return (
        jsonify(
            {
                "usuario_id": usuario_id,
                "email": email,
                "roles": ["ADMIN_PLATAFORMA"],
                "primary_role": "ADMIN_PLATAFORMA",
                "access_token": token,
            }
        ),
        200,
    )


@auth_bp.post("/tenant/login")
def tenant_login():
    data = request.get_json() or {}
    email = _normalize_email(data.get("email"))
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "EMAIL_AND_PASSWORD_REQUIRED"}), 400

    row = db.session.execute(
        text(
            """
            select usuario_id, password_hash, activo
            from usuario
            where email = :email
                limit 1
            """
        ),
        {"email": email},
    ).mappings().first()

    if not row:
        return jsonify({"error": "INVALID_CREDENTIALS"}), 401
    if not row["activo"]:
        return jsonify({"error": "USER_INACTIVE"}), 403
    if not verify_password(password, row["password_hash"]):
        return jsonify({"error": "INVALID_CREDENTIALS"}), 401

    usuario_id = int(row["usuario_id"])

    tenant_ids = _list_tenant_ids_for_user(usuario_id)
    if not tenant_ids:
        return jsonify({"error": "NO_TENANT_ACCESS"}), 403

    _update_last_login_usuario(usuario_id)

    token = _issue_tenant_base_token(usuario_id, tenant_ids)

    return (
        jsonify(
            {
                "usuario_id": usuario_id,
                "email": email,
                "tenant_ids": tenant_ids,
                "access_token": token,
            }
        ),
        200,
    )


@auth_bp.post("/tenant/select")
def tenant_select():
    data = request.get_json() or {}
    usuario_id = data.get("usuario_id")
    empresa_id = data.get("empresa_id")

    if not usuario_id or not empresa_id:
        return jsonify({"error": "USUARIO_ID_AND_EMPRESA_ID_REQUIRED"}), 400

    usuario_id = int(usuario_id)
    empresa_id = int(empresa_id)

    member = db.session.execute(
        text(
            """
            select 1
            from empresa_usuario
            where empresa_id = :e and usuario_id = :u and activo = true
                limit 1
            """
        ),
        {"e": empresa_id, "u": usuario_id},
    ).first()

    if not member:
        return jsonify({"error": "TENANT_ACCESS_DENIED"}), 403

    roles = _get_tenant_roles(empresa_id, usuario_id)
    if not roles:
        roles = ["USER"]

    token = _issue_tenant_token(usuario_id, empresa_id, roles)

    return (
        jsonify(
            {
                "usuario_id": usuario_id,
                "empresa_id": empresa_id,
                "roles": roles,
                "primary_role": _primary_role(roles),
                "access_token": token,
            }
        ),
        200,
    )


@auth_bp.post("/client/signup")
def client_signup():
    data = request.get_json() or {}

    empresa_id = data.get("empresa_id")
    email = _normalize_email(data.get("email"))
    password = data.get("password") or ""
    nombre_razon = (data.get("nombre_razon") or "").strip()
    nit_ci = (data.get("nit_ci") or "").strip() or None
    telefono = (data.get("telefono") or "").strip() or None

    if not empresa_id or not email or not password or not nombre_razon:
        return jsonify({"error": "EMPRESA_ID_EMAIL_PASSWORD_NOMBRE_REQUIRED"}), 400

    if not _password_ok(password):
        return jsonify({"error": "PASSWORD_8_72_BYTES"}), 400

    empresa_id = int(empresa_id)

    empresa_ok = db.session.execute(
        text("select 1 from empresa where empresa_id=:e limit 1"),
        {"e": empresa_id},
    ).first()
    if not empresa_ok:
        return jsonify({"error": "EMPRESA_NOT_FOUND"}), 404

    exists = db.session.execute(
        text("select 1 from cliente where email=:email limit 1"),
        {"email": email},
    ).first()
    if exists:
        return jsonify({"error": "EMAIL_ALREADY_EXISTS"}), 409

    pw_hash = hash_password(password)

    row = db.session.execute(
        text(
            """
            insert into cliente
            (empresa_id, email, password_hash, nombre_razon, nit_ci, telefono, activo, creado_en)
            values
                (:empresa_id, :email, :pw, :nombre, :nit, :tel, true, now())
                returning cliente_id
            """
        ),
        {
            "empresa_id": empresa_id,
            "email": email,
            "pw": pw_hash,
            "nombre": nombre_razon,
            "nit": nit_ci,
            "tel": telefono,
        },
    ).first()

    cliente_id = int(row[0])
    db.session.commit()

    token = _issue_client_token(cliente_id, empresa_id)

    return (
        jsonify(
            {
                "cliente_id": cliente_id,
                "empresa_id": empresa_id,
                "email": email,
                "roles": ["CLIENTE"],
                "primary_role": "CLIENTE",
                "access_token": token,
            }
        ),
        201,
    )


@auth_bp.post("/client/login")
def client_login():
    data = request.get_json() or {}
    email = _normalize_email(data.get("email"))
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "EMAIL_AND_PASSWORD_REQUIRED"}), 400

    row = db.session.execute(
        text(
            """
            select cliente_id, empresa_id, password_hash, activo
            from cliente
            where email = :email
                limit 1
            """
        ),
        {"email": email},
    ).mappings().first()

    if not row:
        return jsonify({"error": "INVALID_CREDENTIALS"}), 401
    if not row["activo"]:
        return jsonify({"error": "CLIENT_INACTIVE"}), 403
    if not verify_password(password, row["password_hash"]):
        return jsonify({"error": "INVALID_CREDENTIALS"}), 401

    cliente_id = int(row["cliente_id"])
    empresa_id = int(row["empresa_id"])

    _update_last_login_cliente(cliente_id)

    token = _issue_client_token(cliente_id, empresa_id)

    return (
        jsonify(
            {
                "cliente_id": cliente_id,
                "empresa_id": empresa_id,
                "email": email,
                "roles": ["CLIENTE"],
                "primary_role": "CLIENTE",
                "access_token": token,
            }
        ),
        200,
    )


@auth_bp.post("/logout")
def logout():
    return jsonify({"ok": True}), 200
