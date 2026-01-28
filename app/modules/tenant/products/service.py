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
    list_product_suppliers,      # ✅
    replace_product_suppliers, 
)
from app.database.models.proveedor import Proveedor
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

try:
    from app.modules.tenant.products.repository import get_primary_image_url
except ImportError:
    get_primary_image_url = None

try:
    from app.modules.notifications.service import NotificationsService
except ImportError:
    NotificationsService = None

def _resolve_primary_image_url(p, d: dict):
    if callable(get_primary_image_url):
        return get_primary_image_url(p.empresa_id, p.producto_id)
    return d.get("image_url")

def _should_fire_stock_zero(prev_stock, new_stock):
    if NotificationsService and hasattr(NotificationsService, "should_fire_stock_zero"):
        try:
            return NotificationsService.should_fire_stock_zero(prev_stock, new_stock)
        except Exception:
            pass
    if new_stock is None:
        return False
    if prev_stock is None:
        return int(new_stock) == 0
    return int(prev_stock) != 0 and int(new_stock) == 0

def _notify_stock_zero(empresa_id: int, p):
    if not NotificationsService or not hasattr(NotificationsService, "notify_stock_zero"):
        return
    NotificationsService.notify_stock_zero(
        empresa_id=int(empresa_id),
        producto_id=int(p.producto_id),
        codigo=getattr(p, "codigo", None),
        descripcion=getattr(p, "descripcion", None),
    )

def _with_image(p):
    d = p.to_dict()
    d["primary_image_url"] = _resolve_primary_image_url(p, d)
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
        p = create_product(empresa_id, payload)
        db.session.commit()

        if "stock" in payload and payload.get("stock") is not None:
            new_stock = getattr(p, "stock", None)
            if _should_fire_stock_zero(None, new_stock):
                _notify_stock_zero(int(empresa_id), p)

        return _with_image(p), None
    except ValueError:
        db.session.rollback()
        return None, "invalid_image_url"
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

    prev_stock = getattr(p, "stock", None)

    try:
        update_product(p, payload)
        db.session.commit()

        if "stock" in payload and payload.get("stock") is not None:
            new_stock = getattr(p, "stock", None)
            if _should_fire_stock_zero(prev_stock, new_stock):
                _notify_stock_zero(int(empresa_id), p)

        return _with_image(p), None
    except ValueError:
        db.session.rollback()
        return None, "invalid_image_url"
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_delete_product(empresa_id: int, producto_id: int):
    p = get_product_any(empresa_id, producto_id)
    if not p:
        return False
    soft_delete_product(p)
    db.session.commit()
    return True

def tenant_restore_product(empresa_id: int, producto_id: int):
    p = get_product_any(empresa_id, producto_id)
    if not p:
        return None
    restore_product(p)
    db.session.commit()
    return _with_image(p)
def tenant_list_product_suppliers(empresa_id: int, producto_id: int, include_inactivos: bool = False):
    p = get_product_any(empresa_id, producto_id)
    if not p:
        return None, "not_found"

    rows = list_product_suppliers(empresa_id, producto_id, include_inactivos=include_inactivos)
    return {"items": [r.to_dict() for r in rows]}, None


def tenant_set_product_suppliers(empresa_id: int, producto_id: int, payload: dict):
    empresa_id = int(empresa_id)
    producto_id = int(producto_id)

    proveedor_ids = payload.get("proveedor_ids", [])
    if not isinstance(proveedor_ids, list):
        return None, "invalid_payload"

    # normaliza ids
    clean_ids: list[int] = []
    for x in proveedor_ids:
        try:
            n = int(x)
            if n > 0:
                clean_ids.append(n)
        except Exception:
            pass
    clean_ids = sorted(set(clean_ids))

    try:
        replace_product_suppliers(empresa_id, producto_id, clean_ids)
        db.session.commit()
        return {"ok": True, "proveedor_ids": clean_ids}, None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"
    except SQLAlchemyError:
        db.session.rollback()
        return None, "save_failed"
