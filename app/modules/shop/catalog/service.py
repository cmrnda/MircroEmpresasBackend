from app.modules.shop.catalog.repository import (
    list_categories,
    list_products,
    get_product,
)


def shop_list_categories(empresa_id: int):
    return [c.to_dict() for c in list_categories(empresa_id)]


def shop_list_products(empresa_id: int, q=None, categoria_id=None, page=1, page_size=20):
    items, total = list_products(empresa_id, q=q, categoria_id=categoria_id, page=page, page_size=page_size)
    out = []
    for p in items:
        d = p.to_dict()
        d["primary_image_url"] = d.get("image_url")
        d["cantidad_actual"] = d.get("stock")
        out.append(d)
    return {"items": out, "page": int(page), "page_size": int(page_size), "total": int(total)}


def shop_get_product(empresa_id: int, producto_id: int):
    p = get_product(empresa_id, producto_id)
    if not p:
        return None
    d = p.to_dict()
    d["primary_image_url"] = d.get("image_url")
    d["cantidad_actual"] = d.get("stock")
    return d
