from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id
from app.modules.tenant.products.service import (
    tenant_list_products,
    tenant_get_product,
    tenant_create_product,
    tenant_update_product,
    tenant_delete_product,
    tenant_restore_product,
)

bp = Blueprint("tenant_products_api", __name__, url_prefix="/tenant/products")

def _error_code(err: str) -> int:
    if err == "conflict":
        return 409
    if err == "not_found":
        return 404
    return 400

@bp.get("")
@jwt_required()
@require_tenant_admin
def list_products():
    empresa_id = int(current_empresa_id())
    q = (request.args.get("q") or "").strip() or None
    categoria_id = request.args.get("categoria_id")
    categoria_id = int(categoria_id) if categoria_id and str(categoria_id).strip().isdigit() else None
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    items = tenant_list_products(empresa_id, q=q, categoria_id=categoria_id, include_inactivos=include_inactivos)
    return jsonify({"items": items}), 200

@bp.get("/<int:producto_id>")
@jwt_required()
@require_tenant_admin
def get_product(producto_id: int):
    empresa_id = int(current_empresa_id())
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    data = tenant_get_product(empresa_id, producto_id, include_inactivos=include_inactivos)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_tenant_admin
def create_product():
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_create_product(empresa_id, payload)
    if err:
        return jsonify({"error": err}), _error_code(err)
    return jsonify(data), 201

@bp.put("/<int:producto_id>")
@jwt_required()
@require_tenant_admin
def update_product(producto_id: int):
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_update_product(empresa_id, producto_id, payload)
    if err:
        return jsonify({"error": err}), _error_code(err)
    return jsonify(data), 200

@bp.delete("/<int:producto_id>")
@jwt_required()
@require_tenant_admin
def delete_product(producto_id: int):
    empresa_id = int(current_empresa_id())
    ok = tenant_delete_product(empresa_id, producto_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200

@bp.post("/<int:producto_id>/restore")
@jwt_required()
@require_tenant_admin
def restore_product(producto_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_restore_product(empresa_id, producto_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200
