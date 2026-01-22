from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id
from app.modules.tenant.categories.service import (
    tenant_list_categories,
    tenant_get_category,
    tenant_create_category,
    tenant_update_category,
    tenant_delete_category,
    tenant_restore_category,
)

bp = Blueprint("tenant_categories_api", __name__, url_prefix="/tenant/categories")

@bp.get("")
@jwt_required()
@require_tenant_admin
def list_categories():
    empresa_id = int(current_empresa_id())
    q = (request.args.get("q") or "").strip() or None
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    return jsonify({"items": tenant_list_categories(empresa_id, q=q, include_inactivos=include_inactivos)}), 200

@bp.get("/<int:categoria_id>")
@jwt_required()
@require_tenant_admin
def get_category(categoria_id: int):
    empresa_id = int(current_empresa_id())
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    data = tenant_get_category(empresa_id, categoria_id, include_inactivos=include_inactivos)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_tenant_admin
def create_category():
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_create_category(empresa_id, payload)
    if err:
        code = 409 if err == "conflict" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 201

@bp.put("/<int:categoria_id>")
@jwt_required()
@require_tenant_admin
def update_category(categoria_id: int):
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_update_category(empresa_id, categoria_id, payload)
    if err:
        code = 409 if err == "conflict" else 404
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.delete("/<int:categoria_id>")
@jwt_required()
@require_tenant_admin
def delete_category(categoria_id: int):
    empresa_id = int(current_empresa_id())
    ok = tenant_delete_category(empresa_id, categoria_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200

@bp.post("/<int:categoria_id>/restore")
@jwt_required()
@require_tenant_admin
def restore_category(categoria_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_restore_category(empresa_id, categoria_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200
