from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_platform_admin
from app.modules.platform.tenants.service import (
    platform_list_tenants,
    platform_get_tenant,
    platform_create_tenant,
    platform_update_tenant,
    platform_delete_tenant,
)

bp = Blueprint("platform_tenants_api", __name__, url_prefix="/platform/tenants")

@bp.get("")
@jwt_required()
@require_platform_admin
def list_tenants():
    q = (request.args.get("q") or "").strip() or None
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    return jsonify({"items": platform_list_tenants(q=q, include_inactivos=include_inactivos)}), 200

@bp.get("/<int:empresa_id>")
@jwt_required()
@require_platform_admin
def get_tenant(empresa_id: int):
    data = platform_get_tenant(empresa_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_platform_admin
def create_tenant():
    payload = request.get_json(silent=True) or {}
    data, err = platform_create_tenant(payload)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(data), 201

@bp.put("/<int:empresa_id>")
@jwt_required()
@require_platform_admin
def update_tenant(empresa_id: int):
    payload = request.get_json(silent=True) or {}
    data = platform_update_tenant(empresa_id, payload)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.delete("/<int:empresa_id>")
@jwt_required()
@require_platform_admin
def delete_tenant(empresa_id: int):
    ok = platform_delete_tenant(empresa_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200
