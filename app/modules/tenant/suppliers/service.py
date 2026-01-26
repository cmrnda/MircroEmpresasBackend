from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.tenant.suppliers.repository import (
    list_suppliers,
    get_supplier,
    get_supplier_any,
    create_supplier,
    update_supplier,
    soft_delete_supplier,
    restore_supplier,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

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