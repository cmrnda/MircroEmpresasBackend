from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.common.authz import require_seller
from app.common.tenant_context import current_empresa_id
from app.modules.orders import bp
from app.modules.orders.service import (
    tenant_list_orders,
    tenant_get_order,
    tenant_ship_order,
    tenant_complete_order,
)

@bp.get("")
@jwt_required()
@require_seller
def list_orders():
    empresa_id = current_empresa_id()
    estado = request.args.get("estado")
    page = request.args.get("page", 1)
    page_size = request.args.get("page_size", 20)
    return jsonify(tenant_list_orders(empresa_id, estado, page, page_size)), 200

@bp.get("/<int:venta_id>")
@jwt_required()
@require_seller
def get_order(venta_id):
    empresa_id = current_empresa_id()
    res = tenant_get_order(empresa_id, venta_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200

@bp.patch("/<int:venta_id>/ship")
@jwt_required()
@require_seller
def ship_order(venta_id):
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res, err = tenant_ship_order(empresa_id, venta_id, data)
    if err:
        if err == "unauthorized":
            return jsonify({"error": err}), 401
        if err in ("not_found", "envio_not_found"):
            return jsonify({"error": err}), 404
        return jsonify({"error": err}), 400
    return jsonify(res), 200

@bp.patch("/<int:venta_id>/complete")
@jwt_required()
@require_seller
def complete_order(venta_id):
    empresa_id = current_empresa_id()
    res, err = tenant_complete_order(empresa_id, venta_id)
    if err:
        if err == "unauthorized":
            return jsonify({"error": err}), 401
        if err in ("not_found", "envio_not_found"):
            return jsonify({"error": err}), 404
        return jsonify({"error": err}), 400
    return jsonify(res), 200
