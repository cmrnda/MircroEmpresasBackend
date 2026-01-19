from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.products.repository import (
    list_products,
    get_product,
    get_product_any,
    get_active_category,
    create_product,
    update_product,
    soft_delete_product,
    restore_product,
)

def _prod_dict(p):
    return {
        "producto_id": int(p.producto_id),
        "empresa_id": int(p.empresa_id),
        "categoria_id": int(p.categoria_id),
        "codigo": p.codigo,
        "descripcion": p.descripcion,
        "precio": float(p.precio) if p.precio is not None else 0.0,
        "stock_min": int(p.stock_min),
        "activo": bool(p.activo),
    }

def tenant_list_products(empresa_id: int, include_inactivos: bool, categoria_id=None, q=None):
    return [_prod_dict(p) for p in list_products(empresa_id, include_inactivos, categoria_id, q)]

def tenant_get_product(empresa_id: int, producto_id: int, include_inactivos: bool = False):
    p = get_product(empresa_id, producto_id, include_inactivos)
    return _prod_dict(p) if p else None

def tenant_create_product(empresa_id: int, payload: dict):
    codigo = (payload.get("codigo") or "").strip()
    descripcion = (payload.get("descripcion") or "").strip()
    categoria_id = payload.get("categoria_id")
    precio = payload.get("precio")

    if not codigo or not descripcion or categoria_id is None or precio is None:
        return None, "invalid_payload"

    # categoría debe existir y estar activa (en la misma empresa)
    cat = get_active_category(empresa_id, int(categoria_id))
    if not cat:
        return None, "categoria_not_found"

    try:
        p = create_product(empresa_id, payload)
        return _prod_dict(p), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_update_product(empresa_id: int, producto_id: int, payload: dict):
    p = get_product(empresa_id, producto_id, include_inactivos=False)
    if not p:
        return None

    # si cambian categoria_id, valida que exista y esté activa
    if payload.get("categoria_id") is not None:
        cat = get_active_category(empresa_id, int(payload.get("categoria_id")))
        if not cat:
            return {"error": "categoria_not_found"}

    try:
        updated = update_product(p, payload)
        return _prod_dict(updated)
    except IntegrityError:
        db.session.rollback()
        return {"error": "conflict"}

def tenant_delete_product(empresa_id: int, producto_id: int):
    p = get_product_any(empresa_id, producto_id)
    if not p:
        return False
    if not p.activo:
        return True
    soft_delete_product(p)
    return True

def tenant_restore_product(empresa_id: int, producto_id: int):
    p = get_product_any(empresa_id, producto_id)
    if not p:
        return None
    if p.activo:
        return _prod_dict(p)
    return _prod_dict(restore_product(p))
