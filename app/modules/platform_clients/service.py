from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.platform_clients.repository import (
    list_platform_clients,
    get_client_by_id,
    get_client_by_empresa,
    create_client_for_empresa,
    update_client_model,
    soft_delete_client,
    restore_client,
)


def platform_list_clients(empresa_id: int | None, include_inactivos: bool):
    return [c.to_dict() for c in list_platform_clients(empresa_id, include_inactivos)]


def platform_get_client(cliente_id: int):
    c = get_client_by_id(cliente_id)
    return c.to_dict() if c else None


def platform_list_clients_by_empresa(empresa_id: int, include_inactivos: bool):
    return [c.to_dict() for c in list_platform_clients(empresa_id, include_inactivos)]


def platform_create_client(empresa_id: int, payload: dict):
    email = (payload.get("email") or "").strip()
    password = payload.get("password")
    nombre_razon = (payload.get("nombre_razon") or "").strip()

    if not email or not password or not nombre_razon:
        return None, "invalid_payload"

    try:
        c = create_client_for_empresa(empresa_id, payload)
        return c.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"


def platform_update_client(empresa_id: int, cliente_id: int, payload: dict):
    c = get_client_by_empresa(empresa_id, cliente_id)
    if not c:
        return None

    try:
        updated = update_client_model(c, payload)
        return updated.to_dict()
    except IntegrityError:
        db.session.rollback()
        return {"error": "conflict"}


def platform_delete_client(empresa_id: int, cliente_id: int):
    c = get_client_by_empresa(empresa_id, cliente_id)
    if not c:
        return False
    if not c.activo:
        return True  # idempotente

    soft_delete_client(c)
    return True


def platform_restore_client(empresa_id: int, cliente_id: int):
    c = get_client_by_empresa(empresa_id, cliente_id)
    if not c:
        return None
    if c.activo:
        return c.to_dict()

    return restore_client(c).to_dict()
