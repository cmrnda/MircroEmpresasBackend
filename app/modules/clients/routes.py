from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.tenant_context import current_empresa_id
from app.modules.clients.service import tenant_list_clients, tenant_create_client, tenant_update_client, tenant_delete_client

bp = Blueprint("clients", __name__, url_prefix="/tenant/clients")

@bp.get("")
@jwt_required()
@require_tenant_admin
def list_clients():
    empresa_id = current_empresa_id()
    return jsonify(tenant_list_clients(empresa_id)), 200

@bp.post("")
@jwt_required()
@require_tenant_admin
def create_client():
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res, err = tenant_create_client(empresa_id, data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(res), 201

@bp.put("/<int:cliente_id>")
@jwt_required()
@require_tenant_admin
def update_client(cliente_id):
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res = tenant_update_client(empresa_id, cliente_id, data)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200

@bp.delete("/<int:cliente_id>")
@jwt_required()
@require_tenant_admin
def delete_client(cliente_id):
    empresa_id = current_empresa_id()
    ok = tenant_delete_client(empresa_id, cliente_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200
