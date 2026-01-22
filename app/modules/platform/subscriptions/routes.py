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
    items = platform_list_subscriptions(include_inactivos=include_inactivos)
    return jsonify({"items": items}), 200


@bp.get("/<int:empresa_id>")
@jwt_required()
@require_platform_admin
def get_subscription(empresa_id: int):
    data = platform_get_subscription(empresa_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200


@bp.put("/<int:empresa_id>")
@jwt_required()
@require_platform_admin
def update_subscription(empresa_id: int):
    payload = request.get_json(silent=True) or {}
    data, err = platform_update_subscription(empresa_id, payload)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(data), 200
