from flask import Blueprint, request, jsonify
from app.common.paging import page_args
from app.modules.shop.catalog.service import shop_list_categories, shop_list_products, shop_get_product

bp = Blueprint("shop_catalog_api", __name__, url_prefix="/shop")


@bp.get("/<int:empresa_id>/categories")
def list_categories(empresa_id: int):
    return jsonify(shop_list_categories(empresa_id)), 200


@bp.get("/<int:empresa_id>/products")
def list_products(empresa_id: int):
    q = (request.args.get("q") or "").strip() or None
    categoria_id = request.args.get("categoria_id")
    categoria_id = int(categoria_id) if categoria_id and str(categoria_id).strip().isdigit() else None
    page, page_size = page_args(request.args)
    data = shop_list_products(empresa_id, q=q, categoria_id=categoria_id, page=page, page_size=page_size)
    return jsonify(data), 200


@bp.get("/<int:empresa_id>/products/<int:producto_id>")
def get_product(empresa_id: int, producto_id: int):
    data = shop_get_product(empresa_id, producto_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200
