from app.auth.me_service import change_my_password
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.auth.service import (
    login_platform,
    login_tenant_user,
    login_client,
    logout_current_token,
)

bp = Blueprint("auth_api", __name__, url_prefix="/auth")


def _unpack(result):
    if isinstance(result, tuple) and len(result) == 2:
        return result[0], result[1]
    return result, None


def _get_empresa_id(data):
    return request.headers.get("X-Empresa-Id") or (data or {}).get("empresa_id")


def _error_code(err):
    if err == "empresa_required":
        return 409
    if err in ("invalid_payload", "invalid_empresa_id", "invalid_empresa_header"):
        return 400
    if err == "forbidden_empresa":
        return 403
    return 401


def _login_response(payload, err):
    if err:
        code = _error_code(err)
        if err == "empresa_required":
            return jsonify({"error": err, "data": payload}), code
        return jsonify({"error": err}), code

    if payload is None:
        return jsonify({"error": "invalid_credentials"}), 401

    if isinstance(payload, dict) and payload.get("error"):
        e = payload.get("error")
        code = _error_code(e)
        return jsonify(payload), code

    return jsonify(payload), 200


@bp.post("/platform/login")
def platform_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    payload, err = _unpack(login_platform(email, password))
    return _login_response(payload, err)


@bp.post("/tenant/login")
def tenant_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    empresa_id = _get_empresa_id(data)

    payload, err = _unpack(login_tenant_user(email, password, empresa_id))
    return _login_response(payload, err)


@bp.post("/client/login")
def client_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    empresa_id = _get_empresa_id(data)

    payload, err = _unpack(login_client(email, password, empresa_id))
    return _login_response(payload, err)


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
