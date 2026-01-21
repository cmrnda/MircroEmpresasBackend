from app.extensions import db
from app.modules.tenant.orders.repository import (
    list_orders,
    get_order,
    get_order_details,
    set_shipping,
    set_delivered,
)

def tenant_list_orders(empresa_id: int, estado=None, cliente_id=None):
    rows = list_orders(empresa_id, estado=estado, cliente_id=cliente_id)
    return [v.to_dict() for v in rows]

def tenant_get_order(empresa_id: int, venta_id: int):
    v = get_order(empresa_id, venta_id)
    if not v:
        return None
    det = get_order_details(empresa_id, venta_id)
    data = v.to_dict()
    data["detalle"] = [d.to_dict() for d in det]
    return data

def tenant_ship_order(empresa_id: int, venta_id: int, payload: dict, usuario_id: int):
    v = get_order(empresa_id, venta_id)
    if not v:
        return None, "not_found"
    if v.estado not in ("CREADA", "PAGADA", "CONFIRMADA"):
        return None, "invalid_state"
    with db.session.begin():
        set_shipping(v, payload, usuario_id)
    return tenant_get_order(empresa_id, venta_id), None

def tenant_complete_order(empresa_id: int, venta_id: int, usuario_id: int):
    v = get_order(empresa_id, venta_id)
    if not v:
        return None, "not_found"
    if v.estado not in ("DESPACHADA",):
        return None, "invalid_state"
    with db.session.begin():
        set_delivered(v, usuario_id)
    return tenant_get_order(empresa_id, venta_id), None
