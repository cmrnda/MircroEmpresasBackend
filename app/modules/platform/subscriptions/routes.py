from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_platform_admin
from app.modules.platform.subscriptions.service import (
    platform_list_subscriptions,
    platform_get_subscription,
    platform_update_subscription,
)

bp = Blueprint("platform_subscriptions_api", __name__, url_prefix="/platform/subscriptions")

@bp.get("")
@jwt_required()
@require_platform_admin
def list_subscriptions():
    include_inactivos = (request.args.get("include_inactivos") or "").strip().lower() in ("1", "true", "yes")
    return jsonify({"items": platform_list_subscriptions(include_inactivos=include_inactivos)}), 200

@bp.get("/<int:empresa_id>")
@jwt_required()
@require_platform_admin
def get_subscription(empresa_id: int):
    return jsonify(platform_get_subscription(empresa_id)), 200

@bp.put("/<int:empresa_id>")
@jwt_required()
@require_platform_admin
def update_subscription(empresa_id: int):
    payload = request.get_json(silent=True) or {}
    return jsonify(platform_update_subscription(empresa_id, payload)), 200
