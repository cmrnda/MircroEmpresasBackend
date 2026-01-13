from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.common.authz import require_tenant_admin
from app.common.tenant_context import current_empresa_id
from app.modules.users.service import tenant_list_users, tenant_create_user, tenant_update_user, tenant_delete_user

bp = Blueprint("users", __name__, url_prefix="/tenant/users")


@bp.get("")
@jwt_required()
@require_tenant_admin
def list_users():
    empresa_id = current_empresa_id()
    return jsonify(tenant_list_users(empresa_id)), 200


@bp.post("")
@jwt_required()
@require_tenant_admin
def create_user():
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res, err = tenant_create_user(empresa_id, data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(res), 201


@bp.put("/<int:usuario_id>")
@jwt_required()
@require_tenant_admin
def update_user(usuario_id):
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res = tenant_update_user(empresa_id, usuario_id, data)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200


@bp.delete("/<int:usuario_id>")
@jwt_required()
@require_tenant_admin
def delete_user(usuario_id):
    empresa_id = current_empresa_id()
    ok = tenant_delete_user(empresa_id, usuario_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200
