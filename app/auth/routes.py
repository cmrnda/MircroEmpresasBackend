from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required
)
from sqlalchemy import text
from app.extensions import db
from app.security.password import verify_password, hash_password

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _get_roles(empresa_id: int, usuario_id: int):
    roles = []

    r = db.session.execute(
        text("select 1 from usuario_admin_plataforma where usuario_id=:u limit 1"),
        {"u": usuario_id}
    ).first()
    if r:
        roles.append("ADMIN_PLATAFORMA")

    r = db.session.execute(
        text("select 1 from usuario_admin_empresa where empresa_id=:e and usuario_id=:u limit 1"),
        {"e": empresa_id, "u": usuario_id}
    ).first()
    if r:
        roles.append("ADMIN_EMPRESA")

    r = db.session.execute(
        text("select 1 from usuario_vendedor where empresa_id=:e and usuario_id=:u limit 1"),
        {"e": empresa_id, "u": usuario_id}
    ).first()
    if r:
        roles.append("VENDEDOR")

    return roles


def _primary_role(roles):
    if "ADMIN_PLATAFORMA" in roles:
        return "ADMIN_PLATAFORMA"
    if "ADMIN_EMPRESA" in roles:
        return "ADMIN_EMPRESA"
    if "VENDEDOR" in roles:
        return "VENDEDOR"
    return "USER"


def _is_admin_plataforma(usuario_id: int) -> bool:
    r = db.session.execute(
        text("select 1 from usuario_admin_plataforma where usuario_id=:u limit 1"),
        {"u": usuario_id}
    ).first()
    return bool(r)


def _require_fields(data, fields):
    missing = [f for f in fields if not data.get(f)]
    return missing


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    empresa_id = data.get("empresa_id")
    email = data.get("email")
    password = data.get("password")

    missing = _require_fields(data, ["empresa_id", "email", "password"])
    if missing:
        return jsonify({"error": "campos_requeridos", "fields": missing}), 400

    row = db.session.execute(
        text("""
             select usuario_id, password_hash, activo
             from usuario
             where email = :email
                 limit 1
             """),
        {"email": email}
    ).mappings().first()

    if not row:
        return jsonify({"error": "credenciales_invalidas"}), 401

    if not row["activo"]:
        return jsonify({"error": "usuario_inactivo"}), 403

    if not verify_password(password, row["password_hash"]):
        return jsonify({"error": "credenciales_invalidas"}), 401

    roles = _get_roles(int(empresa_id), int(row["usuario_id"]))
    primary_role = _primary_role(roles)

    additional_claims = {
        "empresa_id": int(empresa_id),
        "usuario_id": int(row["usuario_id"]),
        "roles": roles,
        "primary_role": primary_role
    }

    token = create_access_token(identity=str(row["usuario_id"]), additional_claims=additional_claims)

    return jsonify({
        "access_token": token,
        "empresa_id": int(empresa_id),
        "usuario_id": int(row["usuario_id"]),
        "roles": roles,
        "primary_role": primary_role
    }), 200


@auth_bp.post("/signup")
def signup():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    missing = _require_fields(data, ["email", "password"])
    if missing:
        return jsonify({"error": "campos_requeridos", "fields": missing}), 400

    exists = db.session.execute(
        text("select 1 from usuario where email=:email limit 1"),
        {"email": email}
    ).first()
    if exists:
        return jsonify({"error": "email_ya_registrado"}), 409

    pw_hash = hash_password(password)

    row = db.session.execute(
        text("""
             insert into usuario (email, password_hash, activo, creado_en)
             values (:email, :password_hash, true, now())
                 returning usuario_id
             """),
        {"email": email, "password_hash": pw_hash}
    ).mappings().first()

    db.session.commit()

    return jsonify({
        "message": "usuario_creado",
        "usuario_id": int(row["usuario_id"]),
        "email": email
    }), 201


@auth_bp.post("/empresas")
@jwt_required()
def create_empresa():
    data = request.get_json() or {}
    nombre = data.get("nombre")
    nit = data.get("nit")

    missing = _require_fields(data, ["nombre"])
    if missing:
        return jsonify({"error": "campos_requeridos", "fields": missing}), 400

    claims = get_jwt()
    usuario_id = int(claims.get("usuario_id"))

    if not _is_admin_plataforma(usuario_id):
        return jsonify({"error": "forbidden"}), 403

    row = db.session.execute(
        text("""
             insert into empresa (nombre, nit, estado, creado_en)
             values (:nombre, :nit, 'ACTIVA', now())
                 returning empresa_id
             """),
        {"nombre": nombre, "nit": nit}
    ).mappings().first()

    empresa_id = int(row["empresa_id"])

    db.session.execute(
        text("""
             insert into empresa_config (empresa_id, moneda, tasa_impuesto, actualizado_en)
             values (:empresa_id, 'BOB', 13.000, now())
                 on conflict (empresa_id) do nothing
             """),
        {"empresa_id": empresa_id}
    )

    db.session.execute(
        text("""
             insert into usuario_admin_empresa (empresa_id, usuario_id)
             values (:empresa_id, :usuario_id)
                 on conflict do nothing
             """),
        {"empresa_id": empresa_id, "usuario_id": usuario_id}
    )

    db.session.commit()

    return jsonify({
        "message": "empresa_creada",
        "empresa_id": empresa_id
    }), 201


@auth_bp.post("/assign-role")
@jwt_required()
def assign_role():
    data = request.get_json() or {}
    empresa_id = data.get("empresa_id")
    usuario_id_target = data.get("usuario_id")
    role = (data.get("role") or "").upper().strip()

    missing = _require_fields(data, ["empresa_id", "usuario_id", "role"])
    if missing:
        return jsonify({"error": "campos_requeridos", "fields": missing}), 400

    claims = get_jwt()
    actor_id = int(claims.get("usuario_id"))

    if not _is_admin_plataforma(actor_id):
        return jsonify({"error": "forbidden"}), 403

    if role == "ADMIN_EMPRESA":
        db.session.execute(
            text("""
                 insert into usuario_admin_empresa (empresa_id, usuario_id)
                 values (:e, :u)
                     on conflict do nothing
                 """),
            {"e": int(empresa_id), "u": int(usuario_id_target)}
        )
    elif role == "VENDEDOR":
        db.session.execute(
            text("""
                 insert into usuario_vendedor (empresa_id, usuario_id)
                 values (:e, :u)
                     on conflict do nothing
                 """),
            {"e": int(empresa_id), "u": int(usuario_id_target)}
        )
    elif role == "ADMIN_PLATAFORMA":
        db.session.execute(
            text("""
                 insert into usuario_admin_plataforma (usuario_id)
                 values (:u)
                     on conflict do nothing
                 """),
            {"u": int(usuario_id_target)}
        )
    else:
        return jsonify({"error": "rol_invalido"}), 400

    db.session.commit()
    return jsonify({"message": "rol_asignado"}), 200


@auth_bp.post("/logout")
@jwt_required()
def logout():
    return jsonify({"message": "ok"}), 200
