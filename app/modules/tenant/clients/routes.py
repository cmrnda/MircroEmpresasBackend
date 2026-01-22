from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id
from app.modules.tenant.clients.service import (
    tenant_list_clients,
    tenant_get_client,
    tenant_create_client,
    tenant_update_client,
    tenant_unlink_client,
    tenant_restore_link,
)

bp = Blueprint("tenant_clients_api", __name__, url_prefix="/tenant/clients")

@bp.get("")
@jwt_required()
@require_tenant_admin
def list_clients():
    empresa_id = int(current_empresa_id())
    q = (request.args.get("q") or "").strip() or None
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    return jsonify({"items": tenant_list_clients(empresa_id, q=q, include_inactivos=include_inactivos)}), 200

@bp.get("/<int:cliente_id>")
@jwt_required()
@require_tenant_admin
def get_client(cliente_id: int):
    empresa_id = int(current_empresa_id())
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    data = tenant_get_client(empresa_id, cliente_id, include_inactivos=include_inactivos)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_tenant_admin
def create_client():
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_create_client(empresa_id, payload)
    if err:
        code = 409 if err == "conflict" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 201

@bp.put("/<int:cliente_id>")
@jwt_required()
@require_tenant_admin
def update_client(cliente_id: int):
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_update_client(empresa_id, cliente_id, payload)
    if err:
        code = 409 if err == "conflict" else 404
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.delete("/<int:cliente_id>")
@jwt_required()
@require_tenant_admin
def unlink_client(cliente_id: int):
    empresa_id = int(current_empresa_id())
    ok = tenant_unlink_client(empresa_id, cliente_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200

@bp.post("/<int:cliente_id>/restore")
@jwt_required()
@require_tenant_admin
def restore_link(cliente_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_restore_link(empresa_id, cliente_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200
