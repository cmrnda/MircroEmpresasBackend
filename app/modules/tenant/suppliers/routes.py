from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id
from app.modules.tenant.suppliers.service import (
    tenant_list_suppliers,
    tenant_get_supplier,
    tenant_create_supplier,
    tenant_update_supplier,
    tenant_delete_supplier,
    tenant_restore_supplier,
)

bp = Blueprint("tenant_suppliers_api", __name__, url_prefix="/tenant/suppliers")

@bp.get("")
@jwt_required()
@require_tenant_admin
def list_suppliers():
    empresa_id = int(current_empresa_id())
    q = (request.args.get("q") or "").strip() or None
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    return jsonify({"items": tenant_list_suppliers(empresa_id, q=q, include_inactivos=include_inactivos)}), 200

@bp.get("/<int:proveedor_id>")
@jwt_required()
@require_tenant_admin
def get_supplier(proveedor_id: int):
    empresa_id = int(current_empresa_id())
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    data = tenant_get_supplier(empresa_id, proveedor_id, include_inactivos=include_inactivos)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_tenant_admin
def create_supplier():
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_create_supplier(empresa_id, payload)
    if err:
        code = 409 if err == "conflict" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 201

@bp.put("/<int:proveedor_id>")
@jwt_required()
@require_tenant_admin
def update_supplier(proveedor_id: int):
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_update_supplier(empresa_id, proveedor_id, payload)
    if err:
        code = 409 if err == "conflict" else 404
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.delete("/<int:proveedor_id>")
@jwt_required()
@require_tenant_admin
def delete_supplier(proveedor_id: int):
    empresa_id = int(current_empresa_id())
    ok = tenant_delete_supplier(empresa_id, proveedor_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200

@bp.post("/<int:proveedor_id>/restore")
@jwt_required()
@require_tenant_admin
def restore_supplier(proveedor_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_restore_supplier(empresa_id, proveedor_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200
