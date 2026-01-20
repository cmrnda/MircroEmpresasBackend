from flask import request, jsonify

from app.modules.shop import bp
from app.modules.shop.service import (
    public_list_categories,
    public_list_products,
    public_get_product,
)

@bp.get("/<int:empresa_id>/categories")
def list_categories_public(empresa_id):
    return jsonify(public_list_categories(empresa_id)), 200

@bp.get("/<int:empresa_id>/products")
def list_products_public(empresa_id):
    categoria_id = request.args.get("categoria_id")
    q = request.args.get("q")
    page = request.args.get("page", 1)
    page_size = request.args.get("page_size", 20)
    return jsonify(public_list_products(empresa_id, categoria_id, q, page, page_size)), 200

@bp.get("/<int:empresa_id>/products/<int:producto_id>")
def get_product_public(empresa_id, producto_id):
    res = public_get_product(empresa_id, producto_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200
