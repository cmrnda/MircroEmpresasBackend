from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id, current_usuario_id
from app.modules.tenant.purchases.service import (
    tenant_list_purchases,
    tenant_get_purchase,
    tenant_create_purchase,
    tenant_receive_purchase,
    tenant_cancel_purchase,
)

bp = Blueprint("tenant_purchases_api", __name__, url_prefix="/tenant/purchases")

@bp.get("")
@jwt_required()
@require_tenant_admin
def list_purchases():
    empresa_id = int(current_empresa_id())
    proveedor_id = request.args.get("proveedor_id")
    proveedor_id = int(proveedor_id) if proveedor_id and str(proveedor_id).strip().isdigit() else None
    estado = (request.args.get("estado") or "").strip() or None
    return jsonify({"items": tenant_list_purchases(empresa_id, proveedor_id=proveedor_id, estado=estado)}), 200

@bp.get("/<int:compra_id>")
@jwt_required()
@require_tenant_admin
def get_purchase(compra_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_get_purchase(empresa_id, compra_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_tenant_admin
def create_purchase():
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_create_purchase(empresa_id, payload)
    if err:
        code = 409 if err == "conflict" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 201

@bp.post("/<int:compra_id>/receive")
@jwt_required()
@require_tenant_admin
def receive_purchase(compra_id: int):
    empresa_id = int(current_empresa_id())
    usuario_id = int(current_usuario_id())
    data, err = tenant_receive_purchase(empresa_id, compra_id, usuario_id)
    if err:
        code = 404 if err == "not_found" else 409
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.post("/<int:compra_id>/cancel")
@jwt_required()
@require_tenant_admin
def cancel_purchase(compra_id: int):
    empresa_id = int(current_empresa_id())
    data, err = tenant_cancel_purchase(empresa_id, compra_id)
    if err:
        code = 404 if err == "not_found" else 409
        return jsonify({"error": err}), code
    return jsonify(data), 200
