from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id
from app.modules.tenant.product_image.service import tenant_get_image, tenant_set_image, tenant_remove_image

bp = Blueprint("tenant_product_image_api", __name__, url_prefix="/tenant/products")

@bp.get("/<int:producto_id>/image")
@jwt_required()
@require_tenant_admin
def get_image(producto_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_get_image(empresa_id, producto_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.put("/<int:producto_id>/image")
@jwt_required()
@require_tenant_admin
def set_image(producto_id: int):
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_set_image(empresa_id, producto_id, payload)
    if err:
        code = 404 if err == "not_found" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.delete("/<int:producto_id>/image")
@jwt_required()
@require_tenant_admin
def remove_image(producto_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_remove_image(empresa_id, producto_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True, "data": data}), 200
