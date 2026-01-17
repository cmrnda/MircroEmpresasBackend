from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.clients.repository import list_clients, get_client, create_client, update_client, delete_client
from app.modules.clients.repository import get_active_client
from app.modules.clients.repository import get_client, restore_client

def tenant_list_clients(empresa_id):
    return [c.to_dict() for c in list_clients(empresa_id)]

def tenant_create_client(empresa_id: int, payload: dict):
    # Payload mínimo
    email = (payload.get("email") or "").strip()
    password = payload.get("password")
    nombre_razon = (payload.get("nombre_razon") or "").strip()

    if not email or not password or not nombre_razon:
        return None, "invalid_payload"

    try:
        c = create_client(empresa_id, payload)
        return c.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"
#def tenant_create_client(empresa_id, payload):
#    if not payload.get("email") or not payload.get("password") or not payload.get("nombre_razon"):
#        return None, "invalid_payload"
#    try:
#        c = create_client(empresa_id, payload)
 #       return c.to_dict(), None
 #   except IntegrityError:
  #      db.session.rollback()
   #     return None, "conflict"

def tenant_update_client(empresa_id: int, cliente_id: int, payload: dict):
    c = get_client(empresa_id, cliente_id)
    # si no existe o está inactivo, lo tratamos como not_found (para UI)
    if not c or not c.activo:
        return None

    try:
        updated = update_client(c, payload)
        return updated.to_dict()
    except IntegrityError:
        db.session.rollback()
        # Mantengo tu estilo simple: puedes manejarlo en routes si quieres
        return {"error": "conflict"}

def tenant_delete_client(empresa_id: int, cliente_id: int):
    """
    Soft delete idempotente:
    - si no existe => False (404)
    - si ya estaba inactivo => True (200 ok)
    - si estaba activo => lo desactiva y True
    """
    c = get_client(empresa_id, cliente_id)
    if not c:
        return False
    if not c.activo:
        return True

    delete_client(c)
    return True

def tenant_get_client(empresa_id: int, cliente_id: int):
    c = get_active_client(empresa_id, cliente_id)
    if not c:
        return None
    return c.to_dict()

def tenant_restore_client(empresa_id: int, cliente_id: int):
    c = get_client(empresa_id, cliente_id)  # trae aunque esté inactivo
    if not c:
        return None
    if c.activo:
        return c.to_dict()  # idempotente: ya estaba activo
    return restore_client(c).to_dict()

def tenant_list_clients(empresa_id: int, include_inactivos: bool = False):
    return [c.to_dict() for c in list_clients(empresa_id, include_inactivos=include_inactivos)]
