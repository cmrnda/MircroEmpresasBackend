from app.modules.shop.public.repository import (
    list_public_empresas,
    get_public_empresa,
    list_random_products,
    list_random_products_by_empresa,
)


def _empresa_public_dict(row):
    e, s = row
    return {
        "empresa_id": int(e.empresa_id),
        "nombre": e.nombre,
        "nit": e.nit,
        "logo_url": getattr(s, "logo_url", None) if s else None,
        "image_url": getattr(s, "image_url", None) if s else None,
        "descripcion": getattr(s, "descripcion", None) if s else None,
    }


def _product_public_dict(row):
    p, e, s = row
    d = p.to_dict()
    d["primary_image_url"] = d.get("image_url")
    d["cantidad_actual"] = d.get("stock")
    d["empresa_nombre"] = e.nombre
    d["store_logo_url"] = getattr(s, "logo_url", None) if s else None
    d["store_image_url"] = getattr(s, "image_url", None) if s else None
    return d


def shop_public_list_empresas(q=None, page=1, page_size=12):
    rows, total = list_public_empresas(q=q, page=page, page_size=page_size)
    items = [_empresa_public_dict(r) for r in rows]
    return {"items": items, "page": int(page), "page_size": int(page_size), "total": int(total)}


def shop_public_get_empresa(empresa_id: int):
    row = get_public_empresa(int(empresa_id))
    if not row:
        return None
    return _empresa_public_dict(row)


def shop_public_random_products(limit=12):
    rows = list_random_products(limit=limit)
    return {"items": [_product_public_dict(r) for r in rows]}


def shop_public_random_products_empresa(empresa_id: int, limit=12):
    rows = list_random_products_by_empresa(int(empresa_id), limit=limit)
    return {"items": [_product_public_dict(r) for r in rows]}
