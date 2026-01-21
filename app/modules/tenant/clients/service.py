from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.tenant.clients.repository import (
    list_clients_for_tenant,
    get_client,
    get_link,
    create_client,
    update_client,
    link_client,
    unlink_client,
)

def tenant_list_clients(empresa_id: int, q=None, include_inactivos=False):
    items = list_clients_for_tenant(empresa_id, q=q, include_inactivos=include_inactivos)
    return [c.to_dict() for c in items]

def tenant_get_client(empresa_id: int, cliente_id: int, include_inactivos=False):
    link = get_link(empresa_id, cliente_id)
    if not link:
        return None
    if not include_inactivos and not bool(link.activo):
        return None
    c = get_client(cliente_id)
    if not c:
        return None
    if not include_inactivos and not bool(c.activo):
        return None
    d = c.to_dict()
    d["link_activo"] = bool(link.activo)
    return d

def tenant_create_client(empresa_id: int, payload: dict):
    email = (payload.get("email") or "").strip()
    password = payload.get("password")
    nombre_razon = (payload.get("nombre_razon") or "").strip()
    if not email or not password or not nombre_razon:
        return None, "invalid_payload"
    try:
        with db.session.begin():
            c = create_client(payload)
            link_client(empresa_id, c.cliente_id)
        return tenant_get_client(empresa_id, c.cliente_id, include_inactivos=True), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_update_client(empresa_id: int, cliente_id: int, payload: dict):
    d = tenant_get_client(empresa_id, cliente_id, include_inactivos=True)
    if not d:
        return None, "not_found"
    c = get_client(cliente_id)
    try:
        with db.session.begin():
            update_client(c, payload)
        return tenant_get_client(empresa_id, cliente_id, include_inactivos=True), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_unlink_client(empresa_id: int, cliente_id: int):
    with db.session.begin():
        row = unlink_client(empresa_id, cliente_id)
    if not row:
        return False
    return True

def tenant_restore_link(empresa_id: int, cliente_id: int):
    with db.session.begin():
        link_client(empresa_id, cliente_id)
    return tenant_get_client(empresa_id, cliente_id, include_inactivos=True)
