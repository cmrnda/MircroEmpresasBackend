from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.platform.clients.repository import (
    list_clients,
    get_client,
    create_client,
    update_client,
    soft_delete_client,
    link_client_to_tenant,
    unlink_client_from_tenant,
    list_tenants_for_client,
)

def platform_list_clients(empresa_id=None, q=None, include_inactivos=False):
    return [c.to_dict() for c in list_clients(empresa_id=empresa_id, q=q, include_inactivos=include_inactivos)]

def platform_get_client(cliente_id: int):
    c = get_client(int(cliente_id))
    if not c:
        return None
    data = c.to_dict()
    data["tenants"] = list_tenants_for_client(int(cliente_id))
    return data

def platform_create_client(payload: dict):
    email = (payload.get("email") or "").strip()
    password = payload.get("password")
    nombre_razon = (payload.get("nombre_razon") or "").strip()
    if not email or not password or not nombre_razon:
        return None, "invalid_payload"

    empresa_id = payload.get("empresa_id")

    try:
        with db.session.begin():
            c = create_client(payload)
            if empresa_id is not None:
                link_client_to_tenant(int(empresa_id), int(c.cliente_id))
        return platform_get_client(int(c.cliente_id)), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def platform_update_client(cliente_id: int, payload: dict):
    c = get_client(int(cliente_id))
    if not c:
        return None, "not_found"
    try:
        with db.session.begin():
            update_client(c, payload)
        return platform_get_client(int(cliente_id)), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def platform_delete_client(cliente_id: int):
    c = get_client(int(cliente_id))
    if not c:
        return False, "not_found"
    with db.session.begin():
        soft_delete_client(c)
    return True, None

def platform_link_client(empresa_id: int, cliente_id: int):
    c = get_client(int(cliente_id))
    if not c:
        return None, "not_found"
    with db.session.begin():
        link_client_to_tenant(int(empresa_id), int(cliente_id))
    return platform_get_client(int(cliente_id)), None

def platform_unlink_client(empresa_id: int, cliente_id: int):
    row = unlink_client_from_tenant(int(empresa_id), int(cliente_id))
    if not row:
        return None, "not_found"
    db.session.commit()
    return {"ok": True}, None
