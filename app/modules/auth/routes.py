from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.modules.auth.service import (
    signup_platform_admin,
    login_platform,
    login_tenant_user,
    login_client,
    logout_current_token,
    signup_client
)

bp = Blueprint("auth_api", __name__, url_prefix="/auth")


def _err(code):
    return jsonify({"error": code})


@bp.post("/platform/signup")
def platform_signup():
    data = request.get_json(silent=True) or {}
    payload, err = signup_platform_admin(data.get("email"), data.get("password"))
    if err:
        return _err(err), 409 if err == "email_already_exists" else 400
    return jsonify({"usuario": payload}), 201


@bp.post("/platform/login")
def platform_login():
    data = request.get_json(silent=True) or {}
    payload, err = login_platform(data.get("email"), data.get("password"))
    if err:
        return _err(err), 403 if err == "forbidden" else 400
    return jsonify(payload), 200


@bp.post("/tenant/login")
def tenant_login():
    data = request.get_json(silent=True) or {}
    payload, err = login_tenant_user(
        data.get("email"),
        data.get("password"),
        data.get("empresa_id"),
    )
    if err:
        return jsonify({"error": err, "data": payload}), 409 if err == "empresa_required" else 403
    return jsonify(payload), 200


@bp.post("/client/login")
def client_login():
    data = request.get_json(silent=True) or {}
    payload, err = login_client(
        data.get("email"),
        data.get("password"),
        data.get("empresa_id"),
    )
    if err:
        return jsonify({"error": err, "data": payload}), 409 if err == "empresa_required" else 403
    return jsonify(payload), 200


@bp.post("/logout")
@jwt_required()
def logout():
    if not logout_current_token():
        return jsonify({"error": "logout_failed"}), 400
    return jsonify({"ok": True}), 200


@bp.post("/client/signup")
def client_signup():
    payload = request.get_json(silent=True) or {}
    data, err = signup_client(
        email=payload.get("email"),
        password=payload.get("password"),
        empresa_id=payload.get("empresa_id"),
        nombre_razon=payload.get("nombre_razon"),
        telefono=payload.get("telefono"),
    )
    if err:
        return jsonify({"data": None, "error": err}), 400
    return jsonify({"data": data, "error": None}), 201