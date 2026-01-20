from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.common.authz import require_seller
from app.common.tenant_context import current_empresa_id
from app.modules.product_images import bp
from app.modules.product_images.service import (
    tenant_list_product_images,
    tenant_upload_product_image,
    tenant_set_primary_image,
    tenant_delete_product_image,
)


@bp.get("/<int:producto_id>/images")
@jwt_required()
@require_seller
def list_images(producto_id):
    empresa_id = current_empresa_id()
    res, err = tenant_list_product_images(empresa_id, producto_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify(res), 200


@bp.post("/<int:producto_id>/images")
@jwt_required()
@require_seller
def upload_image(producto_id):
    empresa_id = current_empresa_id()
    file = request.files.get("file")
    set_primary = request.form.get("is_primary") in ("1", "true", "True")
    res, err = tenant_upload_product_image(empresa_id, producto_id, file, set_primary)
    if err:
        if err == "not_found":
            return jsonify({"error": err}), 404
        if err in ("invalid_file_type",):
            return jsonify({"error": err}), 400
        return jsonify({"error": err}), 400
    return jsonify(res), 201


@bp.patch("/<int:producto_id>/images/<int:image_id>/primary")
@jwt_required()
@require_seller
def set_primary(producto_id, image_id):
    empresa_id = current_empresa_id()
    res, err = tenant_set_primary_image(empresa_id, producto_id, image_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify(res), 200


@bp.delete("/<int:producto_id>/images/<int:image_id>")
@jwt_required()
@require_seller
def delete_image(producto_id, image_id):
    empresa_id = current_empresa_id()
    res, err = tenant_delete_product_image(empresa_id, producto_id, image_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify(res), 200
