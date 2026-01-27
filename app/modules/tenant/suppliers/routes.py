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
    tenant_link_supplier_product,
    tenant_unlink_supplier_product,
    tenant_list_products_with_suppliers,
)

bp = Blueprint("tenant_suppliers_api", __name__, url_prefix="/tenant/suppliers")


def _int_arg(name: str, default: int) -> int:
    try:
        return int(request.args.get(name, default))
    except Exception:
        return int(default)


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


# ✅ NUEVO: productos + proveedores (many-to-many)
@bp.get("/products")
@jwt_required()
@require_tenant_admin
def list_products_with_suppliers():
    empresa_id = current_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "forbidden"}), 403

    proveedor_id = request.args.get("proveedor_id")
    proveedor_id = int(proveedor_id) if proveedor_id and str(proveedor_id).strip().isdigit() else None

    q = (request.args.get("q") or "").strip() or None
    limit = _int_arg("limit", 50)
    offset = _int_arg("offset", 0)

    data = tenant_list_products_with_suppliers(
        int(empresa_id),
        proveedor_id=proveedor_id,
        q=q,
        limit=limit,
        offset=offset,
    )
    return jsonify({"data": data}), 200
# ✅ Vincular producto a proveedor
@bp.post("/<int:proveedor_id>/products/<int:producto_id>")
@jwt_required()
@require_tenant_admin
def link_supplier_product(proveedor_id: int, producto_id: int):
    empresa_id = current_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "forbidden"}), 403

    data, err = tenant_link_supplier_product(int(empresa_id), proveedor_id, producto_id)
    if err:
        if err in ("supplier_not_found", "product_not_found"):
            return jsonify({"error": err}), 404
        return jsonify({"error": err}), 400

    # 201 si creó vínculo, 200 si ya existía
    code = 201 if data.get("created") else 200
    return jsonify(data), code


# ✅ Desvincular producto de proveedor
@bp.delete("/<int:proveedor_id>/products/<int:producto_id>")
@jwt_required()
@require_tenant_admin
def unlink_supplier_product(proveedor_id: int, producto_id: int):
    empresa_id = current_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "forbidden"}), 403

    data, err = tenant_unlink_supplier_product(int(empresa_id), proveedor_id, producto_id)
    if err:
        if err == "supplier_not_found":
            return jsonify({"error": err}), 404
        if err == "not_linked":
            return jsonify({"error": err}), 404
        return jsonify({"error": err}), 400

    return jsonify(data), 200