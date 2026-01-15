from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.modules.subscriptions.service import tenant_status

bp = Blueprint("tenant_subscription", __name__, url_prefix="/tenant/subscription")

@bp.get("")
@jwt_required()
def my_subscription():
    empresa_id = get_jwt().get("empresa_id")
    return jsonify(tenant_status(empresa_id)), 200
