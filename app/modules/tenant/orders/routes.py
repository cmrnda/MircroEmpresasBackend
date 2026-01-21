from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_seller
from app.common.current import current_empresa_id, current_usuario_id
from app.modules.tenant.orders.service import (
    tenant_list_orders,
    tenant_get_order,
    tenant_ship_order,
    tenant_complete_order,
)

bp = Blueprint("tenant_orders_api", __name__, url_prefix="/tenant/orders")

@bp.get("")
@jwt_required()
@require_seller
def list_orders():
    empresa_id = int(current_empresa_id())
    estado = (request.args.get("estado") or "").strip() or None
    cliente_id = request.args.get("cliente_id")
    cliente_id = int(cliente_id) if cliente_id and str(cliente_id).strip().isdigit() else None
    return jsonify({"items": tenant_list_orders(empresa_id, estado=estado, cliente_id=cliente_id)}), 200

@bp.get("/<int:venta_id>")
@jwt_required()
@require_seller
def get_order(venta_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_get_order(empresa_id, venta_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("/<int:venta_id>/ship")
@jwt_required()
@require_seller
def ship_order(venta_id: int):
    empresa_id = int(current_empresa_id())
    usuario_id = int(current_usuario_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_ship_order(empresa_id, venta_id, payload, usuario_id)
    if err:
        code = 404 if err == "not_found" else 409
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.post("/<int:venta_id>/complete")
@jwt_required()
@require_seller
def complete_order(venta_id: int):
    empresa_id = int(current_empresa_id())
    usuario_id = int(current_usuario_id())
    data, err = tenant_complete_order(empresa_id, venta_id, usuario_id)
    if err:
        code = 404 if err == "not_found" else 409
        return jsonify({"error": err}), code
    return jsonify(data), 200
