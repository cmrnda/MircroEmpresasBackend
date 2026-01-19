from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_seller
from app.common.tenant_context import current_empresa_id
from app.modules.products import bp
from app.modules.products.service import (
    tenant_list_products,
    tenant_get_product,
    tenant_create_product,
    tenant_update_product,
    tenant_delete_product,
    tenant_restore_product,
)

@bp.get("")
@jwt_required()
@require_seller
def list_products():
    empresa_id = current_empresa_id()
    include_inactivos = request.args.get("include_inactivos") in ("1", "true", "True")
    categoria_id = request.args.get("categoria_id")
    q = request.args.get("q")
    return jsonify(tenant_list_products(empresa_id, include_inactivos, categoria_id, q)), 200

@bp.post("")
@jwt_required()
@require_seller
def create_product():
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res, err = tenant_create_product(empresa_id, data)
    if err:
        status = 409 if err == "conflict" else 400
        return jsonify({"error": err}), status
    return jsonify(res), 201

@bp.get("/<int:producto_id>")
@jwt_required()
@require_seller
def get_product(producto_id):
    empresa_id = current_empresa_id()
    include_inactivos = request.args.get("include_inactivos") in ("1", "true", "True")
    res = tenant_get_product(empresa_id, producto_id, include_inactivos=include_inactivos)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200

@bp.put("/<int:producto_id>")
@jwt_required()
@require_seller
def update_product(producto_id):
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res = tenant_update_product(empresa_id, producto_id, data)

    if not res:
        return jsonify({"error": "not_found"}), 404
    if isinstance(res, dict) and res.get("error") == "conflict":
        return jsonify(res), 409
    if isinstance(res, dict) and res.get("error") == "categoria_not_found":
        return jsonify(res), 400

    return jsonify(res), 200

@bp.delete("/<int:producto_id>")
@jwt_required()
@require_seller
def delete_product(producto_id):
    empresa_id = current_empresa_id()
    ok = tenant_delete_product(empresa_id, producto_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200

@bp.patch("/<int:producto_id>/restore")
@jwt_required()
@require_seller
def restore_product(producto_id):
    empresa_id = current_empresa_id()
    res = tenant_restore_product(empresa_id, producto_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200
