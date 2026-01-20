from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.common.authz import require_seller
from app.common.tenant_context import current_empresa_id
from app.modules.inventory import bp
from app.modules.inventory.service import (
    tenant_inventory_list,
    tenant_inventory_adjust,
)

@bp.get("")
@jwt_required()
@require_seller
def list_inventory():
    empresa_id = current_empresa_id()
    q = request.args.get("q")
    page = request.args.get("page", 1)
    page_size = request.args.get("page_size", 20)
    include_inactivos = request.args.get("include_inactivos") in ("1", "true", "True")
    return jsonify(tenant_inventory_list(empresa_id, q, page, page_size, include_inactivos)), 200

@bp.post("/adjust")
@jwt_required()
@require_seller
def adjust_inventory():
    empresa_id = current_empresa_id()
    data = request.get_json(silent=True) or {}
    res, err = tenant_inventory_adjust(empresa_id, data)
    if err:
        if err == "unauthorized":
            return jsonify({"error": err}), 401
        if err == "stock_insuficiente":
            return jsonify({"error": err}), 409
        return jsonify({"error": err}), 400
    return jsonify(res), 200
