from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.modules.shop_orders import bp
from app.modules.shop_orders.service import (
    create_shop_order,
    my_orders,
    my_order_detail,
)

@bp.post("/<int:empresa_id>/orders")
@jwt_required()
def create_order(empresa_id):
    data = request.get_json(silent=True) or {}
    res, err = create_shop_order(empresa_id, data)
    if err:
        if err == "unauthorized":
            return jsonify({"error": err}), 401
        if err == "forbidden":
            return jsonify({"error": err}), 403
        if err in ("stock_insuficiente", "producto_not_found"):
            return jsonify({"error": err}), 409
        return jsonify({"error": err}), 400
    return jsonify(res), 201

@bp.get("/<int:empresa_id>/orders/my")
@jwt_required()
def list_my_orders(empresa_id):
    page = request.args.get("page", 1)
    page_size = request.args.get("page_size", 20)
    res, err = my_orders(empresa_id, page, page_size)
    if err:
        if err == "unauthorized":
            return jsonify({"error": err}), 401
        return jsonify({"error": err}), 403
    return jsonify(res), 200

@bp.get("/<int:empresa_id>/orders/my/<int:venta_id>")
@jwt_required()
def get_my_order(empresa_id, venta_id):
    res, err = my_order_detail(empresa_id, venta_id)
    if err:
        if err == "unauthorized":
            return jsonify({"error": err}), 401
        if err == "forbidden":
            return jsonify({"error": err}), 403
        return jsonify({"error": err}), 404
    return jsonify(res), 200
