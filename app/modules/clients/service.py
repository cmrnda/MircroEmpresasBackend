from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.clients.repository import list_clients, get_client, create_client, update_client, delete_client

def tenant_list_clients(empresa_id):
    return [c.to_dict() for c in list_clients(empresa_id)]

def tenant_create_client(empresa_id, payload):
    if not payload.get("email") or not payload.get("password") or not payload.get("nombre_razon"):
        return None, "invalid_payload"
    try:
        c = create_client(empresa_id, payload)
        return c.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def tenant_update_client(empresa_id, cliente_id, payload):
    c = get_client(empresa_id, cliente_id)
    if not c:
        return None
    return update_client(c, payload).to_dict()

def tenant_delete_client(empresa_id, cliente_id):
    c = get_client(empresa_id, cliente_id)
    if not c:
        return False
    delete_client(c)
    return True
