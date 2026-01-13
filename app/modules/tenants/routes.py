from flask import Blueprint, request, jsonify
from app.common.authz import require_platform_admin
from app.modules.tenants.service import (
    platform_list_tenants,
    platform_create_tenant,
    platform_update_tenant,
    platform_delete_tenant,
    platform_get_tenant,
)

bp = Blueprint("tenants", __name__, url_prefix="/platform/tenants")

@bp.get("")
@require_platform_admin
def list_tenants():
    return jsonify(platform_list_tenants()), 200

@bp.post("")
@require_platform_admin
def create_tenant():
    data = request.get_json(silent=True) or {}
    res, err = platform_create_tenant(data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(res), 201

@bp.get("/<int:empresa_id>")
@require_platform_admin
def get_tenant(empresa_id):
    e = platform_get_tenant(empresa_id)
    if not e:
        return jsonify({"error": "not_found"}), 404
    return jsonify(e), 200

@bp.put("/<int:empresa_id>")
@require_platform_admin
def update_tenant(empresa_id):
    data = request.get_json(silent=True) or {}
    e = platform_update_tenant(empresa_id, data)
    if not e:
        return jsonify({"error": "not_found"}), 404
    return jsonify(e), 200

@bp.delete("/<int:empresa_id>")
@require_platform_admin
def delete_tenant(empresa_id):
    ok = platform_delete_tenant(empresa_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200
