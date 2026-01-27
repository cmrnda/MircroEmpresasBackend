from flask import Blueprint, request, jsonify
from app.common.paging import page_args
from app.modules.shop.public.service import (
    shop_public_list_empresas,
    shop_public_get_empresa,
    shop_public_random_products,
    shop_public_random_products_empresa,
)

bp = Blueprint("shop_public_api", __name__, url_prefix="/shop/public")


@bp.get("/tenants")
def list_tenants():
    q = (request.args.get("q") or "").strip() or None
    page, page_size = page_args(request.args)
    data = shop_public_list_empresas(q=q, page=page, page_size=page_size)
    return jsonify(data), 200


@bp.get("/tenants/<int:empresa_id>")
def get_tenant(empresa_id: int):
    data = shop_public_get_empresa(int(empresa_id))
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200


@bp.get("/products/random")
def random_products():
    limit = int(request.args.get("limit", 12))
    limit = max(1, min(limit, 60))
    data = shop_public_random_products(limit=limit)
    return jsonify(data), 200


@bp.get("/tenants/<int:empresa_id>/products/random")
def random_products_empresa(empresa_id: int):
    limit = int(request.args.get("limit", 12))
    limit = max(1, min(limit, 60))
    data = shop_public_random_products_empresa(int(empresa_id), limit=limit)
    return jsonify(data), 200
