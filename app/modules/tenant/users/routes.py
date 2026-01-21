from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id
from app.modules.tenant.users.service import (
    tenant_list_users,
    tenant_get_user,
    tenant_create_user,
    tenant_update_user,
    tenant_disable_membership,
    tenant_restore_membership,
)

bp = Blueprint("tenant_users_api", __name__, url_prefix="/tenant/users")

@bp.get("")
@jwt_required()
@require_tenant_admin
def list_users():
    empresa_id = int(current_empresa_id())
    q = (request.args.get("q") or "").strip() or None
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    return jsonify({"items": tenant_list_users(empresa_id, q=q, include_inactivos=include_inactivos)}), 200

@bp.get("/<int:usuario_id>")
@jwt_required()
@require_tenant_admin
def get_user(usuario_id: int):
    empresa_id = int(current_empresa_id())
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    data = tenant_get_user(empresa_id, usuario_id, include_inactivos=include_inactivos)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_tenant_admin
def create_user():
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_create_user(empresa_id, payload)
    if err:
        code = 409 if err == "conflict" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 201

@bp.put("/<int:usuario_id>")
@jwt_required()
@require_tenant_admin
def update_user(usuario_id: int):
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_update_user(empresa_id, usuario_id, payload)
    if err:
        code = 409 if err == "conflict" else 404
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.delete("/<int:usuario_id>")
@jwt_required()
@require_tenant_admin
def disable_membership(usuario_id: int):
    empresa_id = int(current_empresa_id())
    ok = tenant_disable_membership(empresa_id, usuario_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200

@bp.post("/<int:usuario_id>/restore")
@jwt_required()
@require_tenant_admin
def restore_membership(usuario_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_restore_membership(empresa_id, usuario_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200
