from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_client
from app.common.current import current_empresa_id, current_cliente_id
from app.modules.shop.orders.service import shop_create_order, shop_list_my_orders, shop_get_my_order

bp = Blueprint("shop_orders_api", __name__, url_prefix="/shop")

@bp.post("/<int:empresa_id>/orders")
@jwt_required()
@require_client
def create_order(empresa_id: int):
    token_empresa_id = int(current_empresa_id())
    if int(empresa_id) != int(token_empresa_id):
        return jsonify({"error": "forbidden_empresa"}), 403
    cliente_id = int(current_cliente_id())
    payload = request.get_json(silent=True) or {}
    data, err = shop_create_order(empresa_id, cliente_id, payload)
    if err:
        code = 403 if err in ("forbidden", "forbidden_empresa") else 409 if err in ("stock_insuficiente",) else 400
        return jsonify({"error": err}), code
    return jsonify(data), 201

@bp.get("/<int:empresa_id>/my/orders")
@jwt_required()
@require_client
def my_orders(empresa_id: int):
    token_empresa_id = int(current_empresa_id())
    if int(empresa_id) != int(token_empresa_id):
        return jsonify({"error": "forbidden_empresa"}), 403
    cliente_id = int(current_cliente_id())
    return jsonify({"items": shop_list_my_orders(empresa_id, cliente_id)}), 200

@bp.get("/<int:empresa_id>/my/orders/<int:venta_id>")
@jwt_required()
@require_client
def my_order(empresa_id: int, venta_id: int):
    token_empresa_id = int(current_empresa_id())
    if int(empresa_id) != int(token_empresa_id):
        return jsonify({"error": "forbidden_empresa"}), 403
    cliente_id = int(current_cliente_id())
    data = shop_get_my_order(empresa_id, cliente_id, venta_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200
