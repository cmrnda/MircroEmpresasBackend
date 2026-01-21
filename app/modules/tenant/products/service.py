from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.tenant.products.repository import (
    list_products,
    get_product,
    get_product_any,
    create_product,
    update_product,
    soft_delete_product,
    restore_product,
    category_exists,
    get_primary_image_url,
)

def _with_image(p):
    d = p.to_dict()
    d["primary_image_url"] = get_primary_image_url(p.empresa_id, p.producto_id)
    d["cantidad_actual"] = d.get("stock")
    return d

def tenant_list_products(empresa_id: int, q=None, categoria_id=None, include_inactivos=False):
    items = list_products(empresa_id, q=q, categoria_id=categoria_id, include_inactivos=include_inactivos)
    return [_with_image(p) for p in items]

def tenant_get_product(empresa_id: int, producto_id: int, include_inactivos=False):
    p = get_product(empresa_id, producto_id, include_inactivos=include_inactivos)
    return _with_image(p) if p else None

def tenant_create_product(empresa_id: int, payload: dict):
    required = ["categoria_id", "codigo", "descripcion"]
    for k in required:
        if payload.get(k) is None or str(payload.get(k)).strip() == "":
            return None, "invalid_payload"
    if not category_exists(empresa_id, int(payload.get("categoria_id"))):
        return None, "invalid_categoria"
    try:
        with db.session.begin():
            p = create_product(empresa_id, payload)
        return _with_image(p), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_update_product(empresa_id: int, producto_id: int, payload: dict):
    p = get_product(empresa_id, producto_id, include_inactivos=False)
    if not p:
        return None, "not_found"
    if "categoria_id" in payload and payload.get("categoria_id") is not None:
        if not category_exists(empresa_id, int(payload.get("categoria_id"))):
            return None, "invalid_categoria"
    try:
        with db.session.begin():
            update_product(p, payload)
        return _with_image(p), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_delete_product(empresa_id: int, producto_id: int):
    p = get_product_any(empresa_id, producto_id)
    if not p:
        return False
    with db.session.begin():
        soft_delete_product(p)
    return True

def tenant_restore_product(empresa_id: int, producto_id: int):
    p = get_product_any(empresa_id, producto_id)
    if not p:
        return None
    with db.session.begin():
        restore_product(p)
    return _with_image(p)
