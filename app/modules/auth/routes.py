from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.common.current import current_usuario_id
from app.modules.auth.service import platform_login, tenant_login, client_login, logout

bp = Blueprint("auth_api", __name__, url_prefix="/auth")

@bp.post("/platform/login")
def login_platform():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""
    data, err = platform_login(email, password)
    if err:
        code = 403 if err == "forbidden" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.post("/tenant/<int:empresa_id>/login")
def login_tenant(empresa_id: int):
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""
    data, err = tenant_login(empresa_id, email, password)
    if err:
        code = 403 if err in ("forbidden",) else 400
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.post("/client/<int:empresa_id>/login")
def login_client(empresa_id: int):
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    password = payload.get("password") or ""
    data, err = client_login(empresa_id, email, password)
    if err:
        code = 403 if err in ("forbidden",) else 400
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.post("/logout")
@jwt_required()
def do_logout():
    c = get_jwt() or {}
    jti = c.get("jti")
    uid = current_usuario_id()
    if not jti:
        return jsonify({"error": "invalid_token"}), 400
    ok = logout(jti, uid)
    if not ok:
        return jsonify({"error": "logout_failed"}), 409
    return jsonify({"ok": True}), 200
