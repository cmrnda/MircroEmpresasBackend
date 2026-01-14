from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_platform_admin
from app.modules.platform_users.service import platform_reset_usuario_password
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.auth.service import login_platform, login_tenant_user, login_client, logout_current_token
from app.auth.me_service import change_my_password
bp = Blueprint("platform_users", __name__, url_prefix="/platform/users")

@bp.post("/<int:usuario_id>/reset-password")
@jwt_required()
@require_platform_admin
def reset_password(usuario_id):
    res, err = platform_reset_usuario_password(usuario_id)
    if err == "not_found":
        return jsonify({"error": err}), 404
    if err:
        return jsonify({"error": err}), 400
    return jsonify(res), 200

@bp.post("/platform/login")
def platform_login():
    data = request.get_json(silent=True) or {}
    res = login_platform(data.get("email"), data.get("password"))
    if not res:
        return jsonify({"error": "invalid_credentials"}), 401
    return jsonify(res), 200


@bp.post("/tenant/login")
def tenant_login():
    data = request.get_json(silent=True) or {}
    empresa_id = data.get("empresa_id") or request.headers.get("X-Empresa-Id")

    res = login_tenant_user(data.get("email"), data.get("password"), empresa_id)

    if isinstance(res, dict) and res.get("error") == "empresa_required":
        return jsonify(res), 409
    if isinstance(res, dict) and res.get("error") == "invalid_empresa_id":
        return jsonify(res), 400
    if not res:
        return jsonify({"error": "invalid_credentials"}), 401

    return jsonify(res), 200


@bp.post("/client/login")
def client_login():
    data = request.get_json(silent=True) or {}
    empresa_id = data.get("empresa_id") or request.headers.get("X-Empresa-Id")

    res = login_client(data.get("email"), data.get("password"), empresa_id)

    if isinstance(res, dict) and res.get("error") == "empresa_required":
        return jsonify(res), 409
    if isinstance(res, dict) and res.get("error") == "invalid_empresa_id":
        return jsonify(res), 400
    if not res:
        return jsonify({"error": "invalid_credentials"}), 401

    return jsonify(res), 200


@bp.post("/logout")
@jwt_required()
def logout():
    ok = logout_current_token()
    if not ok:
        return jsonify({"error": "logout_failed"}), 400
    return jsonify({"ok": True}), 200


@bp.put("/me/password")
@jwt_required()
def me_change_password():
    data = request.get_json(silent=True) or {}
    new_password = data.get("new_password")
    if not new_password:
        return jsonify({"error": "invalid_payload"}), 400

    ok, err = change_my_password(get_jwt(), new_password)
    if not ok:
        return jsonify({"error": err}), 400

    return jsonify({"ok": True}), 200