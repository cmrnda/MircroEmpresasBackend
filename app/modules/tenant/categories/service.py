from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.tenant.categories.repository import (
    list_categories,
    get_category,
    get_category_any,
    create_category,
    update_category,
    soft_delete_category,
    restore_category,
)

def tenant_list_categories(empresa_id: int, q=None, include_inactivos=False):
    items = list_categories(empresa_id, q=q, include_inactivos=include_inactivos)
    return [c.to_dict() for c in items]

def tenant_get_category(empresa_id: int, categoria_id: int, include_inactivos=False):
    c = get_category(empresa_id, categoria_id, include_inactivos=include_inactivos)
    return c.to_dict() if c else None

def tenant_create_category(empresa_id: int, payload: dict):
    nombre = (payload.get("nombre") or "").strip()
    if not nombre:
        return None, "invalid_payload"

    try:
        c = create_category(empresa_id, nombre)
        db.session.commit()
        return c.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_update_category(empresa_id: int, categoria_id: int, payload: dict):
    c = get_category(empresa_id, categoria_id, include_inactivos=False)
    if not c:
        return None, "not_found"

    try:
        update_category(c, payload)
        db.session.commit()
        return c.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_delete_category(empresa_id: int, categoria_id: int):
    c = get_category_any(empresa_id, categoria_id)
    if not c:
        return False

    soft_delete_category(c)
    db.session.commit()
    return True

def tenant_restore_category(empresa_id: int, categoria_id: int):
    c = get_category_any(empresa_id, categoria_id)
    if not c:
        return None

    restore_category(c)
    db.session.commit()
    return c.to_dict()
