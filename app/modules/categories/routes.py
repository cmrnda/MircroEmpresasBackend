from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_seller
from app.common.tenant_context import current_empresa_id
from app.modules.categories import bp
from app.modules.categories.service import (
    tenant_list_categories,
    tenant_get_category,
    tenant_create_category,
    tenant_update_category,
    tenant_delete_category,
    tenant_restore_category,
)

@bp.get("")
@jwt_required()
@require_seller
def list_categories():
    empresa_id = current_empresa_id()
    include_inactivos = request.args.get("include_inactivos") in ("1", "true", "True")
    return jsonify(tenant_list_categories(empresa_id, include_inactivos)), 200

@bp.post("")
@jwt_required()
@require_seller
def create_category():
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res, err = tenant_create_category(empresa_id, data)
    if err:
        return jsonify({"error": err}), 409 if err == "conflict" else 400
    return jsonify(res), 201

@bp.get("/<int:categoria_id>")
@jwt_required()
@require_seller
def get_category(categoria_id):
    empresa_id = current_empresa_id()
    include_inactivos = request.args.get("include_inactivos") in ("1", "true", "True")
    res = tenant_get_category(empresa_id, categoria_id, include_inactivos=include_inactivos)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200

@bp.put("/<int:categoria_id>")
@jwt_required()
@require_seller
def update_category(categoria_id):
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res = tenant_update_category(empresa_id, categoria_id, data)
    if not res:
        return jsonify({"error": "not_found"}), 404
    if isinstance(res, dict) and res.get("error") == "conflict":
        return jsonify(res), 409
    return jsonify(res), 200

@bp.delete("/<int:categoria_id>")
@jwt_required()
@require_seller
def delete_category(categoria_id):
    empresa_id = current_empresa_id()
    ok = tenant_delete_category(empresa_id, categoria_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200

@bp.patch("/<int:categoria_id>/restore")
@jwt_required()
@require_seller
def restore_category(categoria_id):
    empresa_id = current_empresa_id()
    res = tenant_restore_category(empresa_id, categoria_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200
