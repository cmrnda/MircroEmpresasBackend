from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.auth.service import login_platform, login_tenant_user, login_client, logout_current_token

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.post("/platform/login")
def platform_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    res, err = login_platform(email, password)
    if err:
        return jsonify({"error": err}), 401
    return jsonify(res), 200

@bp.post("/tenant/login")
def tenant_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    empresa_id_header = request.headers.get("X-Empresa-Id")
    res, err = login_tenant_user(email, password, empresa_id_header)
    if err == "empresa_required":
        return jsonify({"error": err, "data": res}), 409
    if err:
        code = 400 if err in ["invalid_empresa_header", "forbidden_empresa"] else 401
        return jsonify({"error": err}), code
    return jsonify(res), 200

@bp.post("/client/login")
def client_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    empresa_id_header = request.headers.get("X-Empresa-Id")
    res, err = login_client(email, password, empresa_id_header)
    if err == "empresa_required":
        return jsonify({"error": err, "data": res}), 409
    if err:
        code = 400 if err in ["invalid_empresa_header", "forbidden_empresa"] else 401
        return jsonify({"error": err}), code
    return jsonify(res), 200

@bp.post("/logout")
@jwt_required()
def logout():
    ok = logout_current_token()
    if not ok:
        return jsonify({"error": "logout_failed"}), 400
    return jsonify({"ok": True}), 200
