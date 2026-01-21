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
        with db.session.begin():
            c = create_category(empresa_id, nombre)
        return c.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_update_category(empresa_id: int, categoria_id: int, payload: dict):
    c = get_category(empresa_id, categoria_id, include_inactivos=False)
    if not c:
        return None, "not_found"
    try:
        with db.session.begin():
            update_category(c, payload)
        return c.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_delete_category(empresa_id: int, categoria_id: int):
    c = get_category_any(empresa_id, categoria_id)
    if not c:
        return False
    with db.session.begin():
        soft_delete_category(c)
    return True

def tenant_restore_category(empresa_id: int, categoria_id: int):
    c = get_category_any(empresa_id, categoria_id)
    if not c:
        return None
    with db.session.begin():
        restore_category(c)
    return c.to_dict()
