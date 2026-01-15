from flask import Blueprint, request, jsonify
from app.common.authz import require_platform_admin
from app.modules.subscriptions.service import *

bp = Blueprint("platform_subscriptions", __name__, url_prefix="/platform/subscriptions")

@bp.get("")
@require_platform_admin
def list_all():
    empresa_id = request.args.get("empresa_id", type=int)
    return jsonify(platform_list(empresa_id)), 200

@bp.post("")
@require_platform_admin
def create():
    res, err = platform_create(request.get_json() or {})
    if err:
        return jsonify({"error": err}), 400
    return jsonify(res), 201

@bp.post("/payments")
@require_platform_admin
def pay():
    res, err = platform_pay(request.get_json() or {})
    if err:
        return jsonify({"error": err}), 400
    return jsonify(res), 201
