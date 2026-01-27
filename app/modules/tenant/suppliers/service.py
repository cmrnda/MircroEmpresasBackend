from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.extensions import db
from app.database.models.proveedor import Proveedor
from app.database.models.producto import Producto

from app.modules.tenant.suppliers.repository import (
    list_suppliers,
    get_supplier,
    get_supplier_any,
    create_supplier,
    update_supplier,
    soft_delete_supplier,
    restore_supplier,
)

from app.modules.tenant.suppliers import repository as repo


def tenant_list_suppliers(empresa_id: int, q=None, include_inactivos=False):
    rows = list_suppliers(empresa_id, q=q, include_inactivos=include_inactivos)
    return [r.to_dict() for r in rows]


def tenant_get_supplier(empresa_id: int, proveedor_id: int, include_inactivos=False):
    s = get_supplier(empresa_id, proveedor_id, include_inactivos=include_inactivos)
    return s.to_dict() if s else None


def tenant_create_supplier(empresa_id: int, payload: dict):
    nombre = (payload.get("nombre") or "").strip()
    if not nombre:
        return None, "invalid_payload"
    try:
        with db.session.begin():
            s = create_supplier(empresa_id, payload)
        return s.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"


def tenant_update_supplier(empresa_id: int, proveedor_id: int, payload: dict):
    s = get_supplier_any(empresa_id, proveedor_id)
    if not s:
        return None, "not_found"

    try:
        update_supplier(s, payload)
        db.session.commit()
        return s.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"
    except SQLAlchemyError:
        db.session.rollback()
        return None, "update_failed"


def tenant_delete_supplier(empresa_id: int, proveedor_id: int):
    s = get_supplier_any(empresa_id, proveedor_id)
    if not s:
        return False

    try:
        soft_delete_supplier(s)
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False


def tenant_restore_supplier(empresa_id: int, proveedor_id: int):
    s = get_supplier_any(empresa_id, proveedor_id)
    if not s:
        return None

    try:
        restore_supplier(s)
        db.session.commit()
        return s.to_dict()
    except SQLAlchemyError:
        db.session.rollback()
        return None


# ✅ NUEVO: productos con sus proveedores
def tenant_list_products_with_suppliers(
    empresa_id: int,
    proveedor_id: int | None,
    q: str | None,
    limit: int,
    offset: int,
) -> dict:
    rows = repo.list_products_with_suppliers(
        empresa_id=int(empresa_id),
        proveedor_id=proveedor_id,
        q=q,
        limit=int(limit),
        offset=int(offset),
    )

    by_prod: dict[int, dict] = {}

    for prod, prov in rows:
        pid = int(prod.producto_id)

        if pid not in by_prod:
            by_prod[pid] = {
                "producto": prod.to_dict(),
                "proveedores": [],
            }

        by_prod[pid]["proveedores"].append(prov.to_dict())

    items = list(by_prod.values())

    return {
        "empresa_id": int(empresa_id),
        "proveedor_id": int(proveedor_id) if proveedor_id else None,
        "q": (q or "").strip() or None,
        "limit": int(limit),
        "offset": int(offset),
        "items": items,
    }

def tenant_link_supplier_product(empresa_id: int, proveedor_id: int, producto_id: int):
    empresa_id = int(empresa_id)
    proveedor_id = int(proveedor_id)
    producto_id = int(producto_id)

    # validar proveedor
    sup = (
        db.session.query(Proveedor)
        .filter(Proveedor.empresa_id == empresa_id)
        .filter(Proveedor.proveedor_id == proveedor_id)
        .first()
    )
    if not sup:
        return None, "supplier_not_found"

    # validar producto
    prod = (
        db.session.query(Producto)
        .filter(Producto.empresa_id == empresa_id)
        .filter(Producto.producto_id == producto_id)
        .first()
    )
    if not prod:
        return None, "product_not_found"

    created = repo.link_product_to_supplier(empresa_id, proveedor_id, producto_id)
    return {"ok": True, "created": bool(created)}, None


def tenant_unlink_supplier_product(empresa_id: int, proveedor_id: int, producto_id: int):
    empresa_id = int(empresa_id)
    proveedor_id = int(proveedor_id)
    producto_id = int(producto_id)

    # validar proveedor (opcional, pero te evita borrar basura)
    sup = (
        db.session.query(Proveedor)
        .filter(Proveedor.empresa_id == empresa_id)
        .filter(Proveedor.proveedor_id == proveedor_id)
        .first()
    )
    if not sup:
        return None, "supplier_not_found"

    ok = repo.unlink_product_from_supplier(empresa_id, proveedor_id, producto_id)
    if not ok:
        return None, "not_linked"

    return {"ok": True}, None