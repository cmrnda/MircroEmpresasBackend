from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.modules.orders.repository import (
    list_ventas,
    get_venta,
    get_envio,
    list_detalles,
    set_envio_despachado,
    set_envio_entregado,
    set_venta_estado,
)

def _usuario_id_from_jwt():
    ident = get_jwt_identity()
    if isinstance(ident, dict):
        for k in ("usuario_id", "id", "sub"):
            if ident.get(k) is not None:
                return int(ident.get(k))
        return None
    try:
        return int(ident)
    except Exception:
        return None

def _venta_dict(v):
    return {
        "venta_id": int(v.venta_id),
        "cliente_id": int(v.cliente_id),
        "fecha_hora": v.fecha_hora.isoformat() if v.fecha_hora else None,
        "total": float(v.total) if v.total is not None else 0.0,
        "estado": v.estado,
    }

def _detalle_dict(d):
    return {
        "venta_detalle_id": int(d.venta_detalle_id),
        "producto_id": int(d.producto_id),
        "cantidad": float(d.cantidad) if d.cantidad is not None else 0.0,
        "precio_unit": float(d.precio_unit) if d.precio_unit is not None else 0.0,
        "subtotal": float(d.subtotal) if d.subtotal is not None else 0.0,
    }

def _envio_dict(e):
    if not e:
        return None
    return {
        "envio_id": int(e.envio_id),
        "departamento": e.departamento,
        "ciudad": e.ciudad,
        "direccion_linea": e.direccion_linea,
        "estado_envio": e.estado_envio,
        "tracking": e.tracking,
        "fecha_despacho": e.fecha_despacho.isoformat() if e.fecha_despacho else None,
        "fecha_entrega": e.fecha_entrega.isoformat() if e.fecha_entrega else None,
    }

def tenant_list_orders(empresa_id: int, estado: str | None, page: int, page_size: int):
    items, total, page, page_size = list_ventas(empresa_id, estado, page, page_size)
    return {
        "items": [_venta_dict(v) for v in items],
        "page": int(page),
        "page_size": int(page_size),
        "total": int(total),
    }

def tenant_get_order(empresa_id: int, venta_id: int):
    v = get_venta(empresa_id, venta_id)
    if not v:
        return None
    detalles = list_detalles(empresa_id, venta_id)
    envio = get_envio(empresa_id, venta_id)
    return {
        "venta": _venta_dict(v),
        "detalles": [_detalle_dict(d) for d in detalles],
        "envio": _envio_dict(envio),
    }

def tenant_ship_order(empresa_id: int, venta_id: int, payload: dict):
    usuario_id = _usuario_id_from_jwt()
    if not usuario_id:
        return None, "unauthorized"

    v = get_venta(empresa_id, venta_id)
    if not v:
        return None, "not_found"

    envio = get_envio(empresa_id, venta_id)
    if not envio:
        return None, "envio_not_found"

    tracking = (payload.get("tracking") or "").strip() or None

    with db.session.begin():
        set_envio_despachado(envio, tracking)
        set_venta_estado(v, "DESPACHADA", confirmado_por_usuario_id=usuario_id)

    return {"ok": True}, None

def tenant_complete_order(empresa_id: int, venta_id: int):
    usuario_id = _usuario_id_from_jwt()
    if not usuario_id:
        return None, "unauthorized"

    v = get_venta(empresa_id, venta_id)
    if not v:
        return None, "not_found"

    envio = get_envio(empresa_id, venta_id)
    if not envio:
        return None, "envio_not_found"

    with db.session.begin():
        set_envio_entregado(envio)
        set_venta_estado(v, "ENTREGADA", confirmado_por_usuario_id=usuario_id)

    return {"ok": True}, None
