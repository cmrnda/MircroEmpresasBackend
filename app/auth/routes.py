from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from app.extensions import db
from app.security.password import verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def _get_roles(empresa_id: int, usuario_id: int):
    roles = []
    try:
        r = db.session.execute(
            text("select 1 from usuario_admin_plataforma where empresa_id=:e and usuario_id=:u limit 1"),
            {"e": empresa_id, "u": usuario_id}
        ).first()
        if r: roles.append("ADMIN_PLATAFORMA")
    except Exception:
        pass

    try:
        r = db.session.execute(
            text("select 1 from usuario_admin_empresa where empresa_id=:e and usuario_id=:u limit 1"),
            {"e": empresa_id, "u": usuario_id}
        ).first()
        if r: roles.append("ADMIN_EMPRESA")
    except Exception:
        pass

    try:
        r = db.session.execute(
            text("select 1 from usuario_encargado_inventario where empresa_id=:e and usuario_id=:u limit 1"),
            {"e": empresa_id, "u": usuario_id}
        ).first()
        if r: roles.append("ENCARGADO_INVENTARIO")
    except Exception:
        pass

    return roles

def _primary_role(roles):
    if "ADMIN_PLATAFORMA" in roles: return "ADMIN_PLATAFORMA"
    if "ADMIN_EMPRESA" in roles: return "ADMIN_EMPRESA"
    if "ENCARGADO_INVENTARIO" in roles: return "ENCARGADO_INVENTARIO"
    return "USER"

@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    empresa_id = data.get("empresa_id")
    email = data.get("email")
    password = data.get("password")

    if not empresa_id or not email or not password:
        return jsonify({"error": "empresa_id, email y password son requeridos"}), 400

    row = db.session.execute(
        text("""
            select usuario_id, password_hash, activo
            from usuario
            where empresa_id = :empresa_id and email = :email
            limit 1
        """),
        {"empresa_id": empresa_id, "email": email}
    ).mappings().first()

    if not row:
        return jsonify({"error": "credenciales invalidas"}), 401

    if not row["activo"]:
        return jsonify({"error": "usuario inactivo"}), 403

    if not verify_password(password, row["password_hash"]):
        return jsonify({"error": "credenciales invalidas"}), 401

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
