from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.categories.repository import (
    list_categories,
    get_category,
    get_category_any,
    create_category,
    update_category,
    soft_delete_category,
    restore_category,
)

def _cat_dict(c):
    return {
        "categoria_id": int(c.categoria_id),
        "empresa_id": int(c.empresa_id),
        "nombre": c.nombre,
        "activo": bool(c.activo),
    }

def tenant_list_categories(empresa_id: int, include_inactivos: bool = False):
    return [_cat_dict(c) for c in list_categories(empresa_id, include_inactivos)]

def tenant_get_category(empresa_id: int, categoria_id: int, include_inactivos: bool = False):
    c = get_category(empresa_id, categoria_id, include_inactivos)
    return _cat_dict(c) if c else None

def tenant_create_category(empresa_id: int, payload: dict):
    nombre = (payload.get("nombre") or "").strip()
    if not nombre:
        return None, "invalid_payload"

    try:
        c = create_category(empresa_id, nombre)
        return _cat_dict(c), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_update_category(empresa_id: int, categoria_id: int, payload: dict):
    # si está inactiva, la tratamos como not_found para edición normal
    c = get_category(empresa_id, categoria_id, include_inactivos=False)
    if not c:
        return None

    try:
        updated = update_category(c, payload)
        return _cat_dict(updated)
    except IntegrityError:
        db.session.rollback()
        return {"error": "conflict"}

def tenant_delete_category(empresa_id: int, categoria_id: int):
    c = get_category_any(empresa_id, categoria_id)
    if not c:
        return False
    if not c.activo:
        return True  # idempotente
    soft_delete_category(c)
    return True

def tenant_restore_category(empresa_id: int, categoria_id: int):
    c = get_category_any(empresa_id, categoria_id)
    if not c:
        return None
    if c.activo:
        return _cat_dict(c)  # idempotente
    return _cat_dict(restore_category(c))