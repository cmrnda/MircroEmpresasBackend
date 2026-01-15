from app.modules.subscriptions.repository import *

def platform_list(empresa_id=None):
    subs = list_suscripciones_by_empresa(empresa_id) if empresa_id else list_suscripciones()
    return [s.to_dict() for s in subs]

def platform_create(payload):
    empresa_id = payload.get("empresa_id")
    plan_id = payload.get("plan_id")

    if not empresa_id or not plan_id:
        return None, "invalid_payload"

    s = create_suscripcion(empresa_id, plan_id)
    return s.to_dict(), None

def platform_pay(payload):
    empresa_id = payload.get("empresa_id")
    suscripcion_id = payload.get("suscripcion_id")
    monto = payload.get("monto")
    metodo = payload.get("metodo")

    if not empresa_id or not suscripcion_id or not monto or not metodo:
        return None, "invalid_payload"

    p = create_pago(empresa_id, suscripcion_id, monto, metodo)
    return p.to_dict(), None

def tenant_status(empresa_id):
    s = get_suscripcion_activa(empresa_id)
    return s.to_dict() if s else None
