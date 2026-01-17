from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from app.modules.subscriptions.service import tenant_status, tenant_plans, tenant_select_plan, tenant_pay

bp = Blueprint("tenant_subscriptions", __name__, url_prefix="/tenant/subscription")

@bp.get("")
@jwt_required()
def my_subscription():
    empresa_id = int(get_jwt().get("empresa_id"))
    return jsonify(tenant_status(empresa_id)), 200

@bp.get("/plans")
@jwt_required()
def plans():
    return jsonify(tenant_plans()), 200

@bp.post("/select")
@jwt_required()
def select_plan():
    empresa_id = int(get_jwt().get("empresa_id"))
    data = request.get_json(silent=True) or {}
    res, err = tenant_select_plan(empresa_id, data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(res), 201

@bp.post("/payments")
@jwt_required()
def pay():
    empresa_id = int(get_jwt().get("empresa_id"))
    data = request.get_json(silent=True) or {}
    res, err = tenant_pay(empresa_id, data)
    if err:
        code = 404 if err == "not_found" else 400
        return jsonify({"error": err}), code
    return jsonify(res), 201
