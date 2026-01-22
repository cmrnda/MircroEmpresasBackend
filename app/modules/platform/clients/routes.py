from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_platform_admin
from app.common.paging import page_args

from app.modules.platform.clients.service import (
    platform_list_clients,
    platform_get_client,
    platform_create_client,
    platform_update_client,
    platform_delete_client,
    platform_link_client,
    platform_unlink_client,
)

bp = Blueprint("platform_clients_api", __name__, url_prefix="/platform/clients")

@bp.get("")
@jwt_required()
@require_platform_admin
def list_clients():
    empresa_id = request.args.get("empresa_id")
    empresa_id = int(empresa_id) if empresa_id and str(empresa_id).strip().isdigit() else None
    q = (request.args.get("q") or "").strip() or None
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    items = platform_list_clients(empresa_id=empresa_id, q=q, include_inactivos=include_inactivos)
    return jsonify({"items": items}), 200

@bp.get("/<int:cliente_id>")
@jwt_required()
@require_platform_admin
def get_client(cliente_id: int):
    data = platform_get_client(cliente_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_platform_admin
def create_client():
    payload = request.get_json(silent=True) or {}
    data, err = platform_create_client(payload)
    if err:
        code = 409 if err == "conflict" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 201

@bp.put("/<int:cliente_id>")
@jwt_required()
@require_platform_admin
def update_client(cliente_id: int):
    payload = request.get_json(silent=True) or {}
    data, err = platform_update_client(cliente_id, payload)
    if err:
        code = 409 if err == "conflict" else 404
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.delete("/<int:cliente_id>")
@jwt_required()
@require_platform_admin
def delete_client(cliente_id: int):
    ok, err = platform_delete_client(cliente_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify({"ok": True}), 200

@bp.post("/<int:cliente_id>/link/<int:empresa_id>")
@jwt_required()
@require_platform_admin
def link_client(cliente_id: int, empresa_id: int):
    data, err = platform_link_client(empresa_id, cliente_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify(data), 200

@bp.post("/<int:cliente_id>/unlink/<int:empresa_id>")
@jwt_required()
@require_platform_admin
def unlink_client(cliente_id: int, empresa_id: int):
    data, err = platform_unlink_client(empresa_id, cliente_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify(data), 200
