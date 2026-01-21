from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id
from app.modules.tenant.settings.service import tenant_get_settings, tenant_update_settings

bp = Blueprint("tenant_settings_api", __name__, url_prefix="/tenant/settings")

@bp.get("")
@jwt_required()
@require_tenant_admin
def get_settings():
    empresa_id = int(current_empresa_id())
    return jsonify(tenant_get_settings(empresa_id)), 200

@bp.put("")
@jwt_required()
@require_tenant_admin
def update_settings():
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    return jsonify(tenant_update_settings(empresa_id, payload)), 200
