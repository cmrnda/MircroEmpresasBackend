from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_platform_admin
from app.modules.platform.plans.service import (
    platform_list_plans,
    platform_get_plan,
    platform_create_plan,
    platform_update_plan,
)

bp = Blueprint("platform_plans_api", __name__, url_prefix="/platform/plans")

@bp.get("")
@jwt_required()
@require_platform_admin
def list_plans():
    return jsonify({"items": platform_list_plans()}), 200

@bp.get("/<int:plan_id>")
@jwt_required()
@require_platform_admin
def get_plan(plan_id: int):
    data = platform_get_plan(plan_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_platform_admin
def create_plan():
    payload = request.get_json(silent=True) or {}
    data, err = platform_create_plan(payload)
    if err:
        code = 409 if err == "conflict" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 201

@bp.put("/<int:plan_id>")
@jwt_required()
@require_platform_admin
def update_plan(plan_id: int):
    payload = request.get_json(silent=True) or {}
    data, err = platform_update_plan(plan_id, payload)
    if err:
        code = 409 if err == "conflict" else 404
        return jsonify({"error": err}), code
    return jsonify(data), 200
