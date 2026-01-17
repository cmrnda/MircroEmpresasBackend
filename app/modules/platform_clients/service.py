from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.platform_clients.repository import (
    platform_list_clients_repo,
    platform_get_client_repo,
    platform_create_client_repo,
    platform_update_client_repo,
    platform_delete_client_repo,
    platform_restore_client_repo,
)

def platform_list_clients(empresa_id: int | None, q: str | None, include_inactivos: bool):
    return [c.to_dict() for c in platform_list_clients_repo(empresa_id, q=q, include_inactivos=include_inactivos)]

def platform_create_client(payload: dict):
    empresa_id = payload.get("empresa_id")
    email = (payload.get("email") or "").strip()
    password = payload.get("password")
    nombre_razon = (payload.get("nombre_razon") or "").strip()

    if not empresa_id or not email or not password or not nombre_razon:
        return None, "invalid_payload"

    try:
        c = platform_create_client_repo(int(empresa_id), payload)
        return c.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def platform_get_client(cliente_id: int):
    c = platform_get_client_repo(cliente_id)
    return c.to_dict() if c else None

def platform_update_client(cliente_id: int, payload: dict):
    c = platform_get_client_repo(cliente_id)
    if not c:
        return None, "not_found"
    try:
        updated = platform_update_client_repo(c, payload)
        return updated.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def platform_delete_client(cliente_id: int):
    return platform_delete_client_repo(cliente_id)

def platform_restore_client(cliente_id: int):
    c = platform_get_client_repo(cliente_id)
    if not c:
        return None, "not_found"
    return platform_restore_client_repo(c).to_dict(), None
