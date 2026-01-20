from app.modules.shop.repository import (
    list_public_categories,
    list_public_products,
    get_public_product,
)


def _cat_dict(c):
    return {
        "categoria_id": int(c.categoria_id),
        "empresa_id": int(c.empresa_id),
        "nombre": c.nombre,
    }


def _prod_dict(p, cantidad_actual, primary_image_url=None):
    return {
        "producto_id": int(p.producto_id),
        "empresa_id": int(p.empresa_id),
        "categoria_id": int(p.categoria_id),
        "codigo": p.codigo,
        "descripcion": p.descripcion,
        "precio": float(p.precio) if p.precio is not None else 0.0,
        "stock_min": int(p.stock_min),
        "cantidad_actual": float(cantidad_actual) if cantidad_actual is not None else 0.0,
        "primary_image_url": primary_image_url,
    }


def public_list_categories(empresa_id: int):
    return [_cat_dict(c) for c in list_public_categories(empresa_id)]


def public_list_products(empresa_id: int, categoria_id=None, q=None, page=1, page_size=20):
    rows, total, page, page_size = list_public_products(empresa_id, categoria_id, q, page, page_size)
    items = [_prod_dict(p, qty, img) for (p, qty, img) in rows]
    return {
        "items": items,
        "page": int(page),
        "page_size": int(page_size),
        "total": int(total),
    }


def public_get_product(empresa_id: int, producto_id: int):
    row, img = get_public_product(empresa_id, producto_id)
    if not row:
        return None
    p, qty = row
    return _prod_dict(p, qty, img)
