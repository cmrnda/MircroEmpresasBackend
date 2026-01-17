from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_platform_admin
from app.modules.subscriptions.service import platform_list, platform_create, platform_pay

bp = Blueprint("platform_subscriptions", __name__, url_prefix="/platform/subscriptions")

@bp.get("")
@jwt_required()
@require_platform_admin
def list_all():
    empresa_id = request.args.get("empresa_id", type=int)
    return jsonify(platform_list(empresa_id)), 200

@bp.post("")
@jwt_required()
@require_platform_admin
def create():
    res, err = platform_create(request.get_json(silent=True) or {})
    if err:
        return jsonify({"error": err}), 400
    return jsonify(res), 201

@bp.post("/payments")
@jwt_required()
@require_platform_admin
def pay():
    res, err = platform_pay(request.get_json(silent=True) or {})
    if err:
        return jsonify({"error": err}), 400
    return jsonify(res), 201
