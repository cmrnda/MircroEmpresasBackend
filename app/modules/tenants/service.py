from app.modules.tenants.repository import (
    list_empresas,
    get_empresa,
    create_empresa,
    update_empresa,
    delete_empresa,
    create_tenant_admin_user,
)
from app.extensions import db

def platform_list_tenants():
    return [e.to_dict() for e in list_empresas()]

def platform_create_tenant(payload):
    nombre = payload.get("nombre")
    nit = payload.get("nit")
    admin_email = (payload.get("admin") or {}).get("email")
    admin_password = (payload.get("admin") or {}).get("password")

    if not nombre or not admin_email or not admin_password:
        return None, "invalid_payload"

    e = create_empresa(nombre, nit)
    u = create_tenant_admin_user(e.empresa_id, admin_email, admin_password)
    return {"empresa": e.to_dict(), "admin_usuario": u.to_dict()}, None

def platform_update_tenant(empresa_id, payload):
    e = get_empresa(empresa_id)
    if not e:
        return None
    return update_empresa(e, payload.get("nombre"), payload.get("nit"), payload.get("estado")).to_dict()

def platform_delete_tenant(empresa_id):
    e = get_empresa(empresa_id)
    if not e:
        return False
    delete_empresa(e)
    return True

def platform_get_tenant(empresa_id):
    e = get_empresa(empresa_id)
    return e.to_dict() if e else None
