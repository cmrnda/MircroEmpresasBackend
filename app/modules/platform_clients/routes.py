from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_platform_admin
from app.modules.platform_clients.service import (
    platform_list_clients,
    platform_create_client,
    platform_update_client,
    platform_delete_client,
    platform_get_client,
    platform_restore_client,
)

bp = Blueprint("platform_clients", __name__, url_prefix="/platform/clients")


@bp.get("")
@jwt_required()
@require_platform_admin
def list_clients():
    empresa_id = request.args.get("empresa_id")
    q = request.args.get("q") or None
    include_inactivos = request.args.get("include_inactivos") in ("1", "true", "True")

    empresa_id_int = int(empresa_id) if empresa_id else None
    return jsonify(platform_list_clients(empresa_id_int, q=q, include_inactivos=include_inactivos)), 200


@bp.post("")
@jwt_required()
@require_platform_admin
def create_client():
    data = request.get_json(silent=True) or {}
    res, err = platform_create_client(data)
    if err:
        code = 409 if err == "conflict" else 400
        return jsonify({"error": err}), code
    return jsonify(res), 201


@bp.get("/<int:cliente_id>")
@jwt_required()
@require_platform_admin
def get_client(cliente_id: int):
    res = platform_get_client(cliente_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200


@bp.put("/<int:cliente_id>")
@jwt_required()
@require_platform_admin
def update_client(cliente_id: int):
    data = request.get_json(silent=True) or {}
    res, err = platform_update_client(cliente_id, data)
    if err:
        code = 409 if err == "conflict" else (404 if err == "not_found" else 400)
        return jsonify({"error": err}), code
    return jsonify(res), 200


@bp.delete("/<int:cliente_id>")
@jwt_required()
@require_platform_admin
def delete_client(cliente_id: int):
    ok = platform_delete_client(cliente_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200


@bp.patch("/<int:cliente_id>/restore")
@jwt_required()
@require_platform_admin
def restore_client(cliente_id: int):
    res, err = platform_restore_client(cliente_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify(res), 200
