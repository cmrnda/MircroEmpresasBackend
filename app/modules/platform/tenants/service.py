from app.extensions import db
from app.modules.platform.tenants.repository import (
    list_empresas,
    get_empresa,
    create_empresa,
    update_empresa,
    soft_delete_empresa,
    create_tenant_admin_user,
)

def platform_list_tenants(q=None, include_inactivos=False):
    return [e.to_dict() for e in list_empresas(q=q, include_inactivos=include_inactivos)]

def platform_get_tenant(empresa_id: int):
    e = get_empresa(int(empresa_id))
    return e.to_dict() if e else None

def platform_create_tenant(payload: dict):
    nombre = (payload.get("nombre") or "").strip()
    nit = (payload.get("nit") or "").strip() or None
    admin = payload.get("admin") or {}
    admin_email = (admin.get("email") or "").strip()
    admin_password = admin.get("password")

    if not nombre or not admin_email or not admin_password:
        return None, "invalid_payload"

    with db.session.begin():
        e = create_empresa(nombre, nit)
        u = create_tenant_admin_user(e.empresa_id, admin_email, admin_password)

    return {"empresa": e.to_dict(), "admin_usuario": u.to_dict()}, None

def platform_update_tenant(empresa_id: int, payload: dict):
    with db.session.begin():
        e = get_empresa(int(empresa_id))
        if not e:
            return None
        update_empresa(e, payload.get("nombre"), payload.get("nit"), payload.get("estado"))
        return e.to_dict()

def platform_delete_tenant(empresa_id: int):
    with db.session.begin():
        e = get_empresa(int(empresa_id))
        if not e:
            return False
        soft_delete_empresa(e)
        return True
