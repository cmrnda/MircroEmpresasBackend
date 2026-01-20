from decimal import Decimal
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.modules.shop_orders.repository import (
    get_cliente,
    get_productos_for_update,
    ensure_existencia_row,
    create_venta,
    add_venta_detalle,
    create_envio,
    add_movimiento,
    list_my_ventas,
    get_my_venta,
    list_venta_detalles,
    get_envio,
)

class ShopOrderError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code

def _cliente_id_from_jwt():
    ident = get_jwt_identity()
    if isinstance(ident, dict):
        for k in ("cliente_id", "id", "sub"):
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
        "empresa_id": int(v.empresa_id),
        "cliente_id": int(v.cliente_id),
        "fecha_hora": v.fecha_hora.isoformat() if v.fecha_hora else None,
        "total": float(v.total) if v.total is not None else 0.0,
        "descuento_total": float(v.descuento_total) if v.descuento_total is not None else 0.0,
        "estado": v.estado,
        "confirmado_en": v.confirmado_en.isoformat() if v.confirmado_en else None,
    }

def _detalle_dict(d):
    return {
        "venta_detalle_id": int(d.venta_detalle_id),
        "producto_id": int(d.producto_id),
        "cantidad": float(d.cantidad) if d.cantidad is not None else 0.0,
        "precio_unit": float(d.precio_unit) if d.precio_unit is not None else 0.0,
        "descuento": float(d.descuento) if d.descuento is not None else 0.0,
        "subtotal": float(d.subtotal) if d.subtotal is not None else 0.0,
    }

def _envio_dict(e):
    if not e:
        return None
    return {
        "envio_id": int(e.envio_id),
        "departamento": e.departamento,
        "ciudad": e.ciudad,
        "zona_barrio": e.zona_barrio,
        "direccion_linea": e.direccion_linea,
        "referencia": e.referencia,
        "telefono_receptor": e.telefono_receptor,
        "costo_envio": float(e.costo_envio) if e.costo_envio is not None else 0.0,
        "estado_envio": e.estado_envio,
        "tracking": e.tracking,
        "fecha_despacho": e.fecha_despacho.isoformat() if e.fecha_despacho else None,
        "fecha_entrega": e.fecha_entrega.isoformat() if e.fecha_entrega else None,
    }

def _tx_begin():
    if db.session.in_transaction():
        return db.session.begin_nested()
    return db.session.begin()

def create_shop_order(empresa_id: int, payload: dict):
    cliente_id = _cliente_id_from_jwt()
    if not cliente_id:
        return None, "unauthorized"

    items = payload.get("items") or []
    if not isinstance(items, list) or len(items) == 0:
        return None, "invalid_payload"

    envio = payload.get("envio")

    producto_ids = []
    qty_map = {}

    for it in items:
        try:
            pid = int(it.get("producto_id"))
            qty = Decimal(str(it.get("cantidad")))
        except Exception:
            return None, "invalid_payload"

        if qty <= 0:
            return None, "invalid_payload"

        producto_ids.append(pid)
        qty_map[pid] = qty_map.get(pid, Decimal("0")) + qty

    producto_ids = list(set(producto_ids))

    if envio is not None:
        dep = (envio.get("departamento") or "").strip()
        ciu = (envio.get("ciudad") or "").strip()
        dirl = (envio.get("direccion_linea") or "").strip()
        if not dep or not ciu or not dirl:
            return None, "invalid_payload"

    v = None

    try:
        with _tx_begin():
            c = get_cliente(empresa_id, int(cliente_id))
            if not c:
                raise ShopOrderError("forbidden")

            rows = get_productos_for_update(empresa_id, producto_ids)
            if len(rows) != len(producto_ids):
                raise ShopOrderError("producto_not_found")

            precio_map = {}

            for p, _ex in rows:
                precio_map[int(p.producto_id)] = Decimal(str(p.precio))
                ex_row = ensure_existencia_row(empresa_id, int(p.producto_id))
                disponible = Decimal(str(ex_row.cantidad_actual))
                req = qty_map[int(p.producto_id)]
                if disponible < req:
                    raise ShopOrderError("stock_insuficiente")

            total = Decimal("0")
            for pid, qty in qty_map.items():
                total += qty * precio_map[int(pid)]

            v = create_venta(empresa_id, int(cliente_id), total)

            for pid, qty in qty_map.items():
                add_venta_detalle(empresa_id, int(v.venta_id), int(pid), qty, precio_map[int(pid)])
                ex_row = ensure_existencia_row(empresa_id, int(pid))
                ex_row.cantidad_actual = Decimal(str(ex_row.cantidad_actual)) - qty
                add_movimiento(empresa_id, int(pid), "SALIDA_VENTA", qty, "venta", int(v.venta_id), int(cliente_id))

            if envio is not None:
                create_envio(empresa_id, int(v.venta_id), envio)

    except ShopOrderError as e:
        return None, e.code

    return {"venta_id": int(v.venta_id)}, None

def my_orders(empresa_id: int, page: int, page_size: int):
    cliente_id = _cliente_id_from_jwt()
    if not cliente_id:
        return None, "unauthorized"
    c = get_cliente(empresa_id, int(cliente_id))
    if not c:
        return None, "forbidden"

    items, total, page, page_size = list_my_ventas(empresa_id, int(cliente_id), page, page_size)
    return {
        "items": [_venta_dict(v) for v in items],
        "page": int(page),
        "page_size": int(page_size),
        "total": int(total),
    }, None

def my_order_detail(empresa_id: int, venta_id: int):
    cliente_id = _cliente_id_from_jwt()
    if not cliente_id:
        return None, "unauthorized"
    c = get_cliente(empresa_id, int(cliente_id))
    if not c:
        return None, "forbidden"

    v = get_my_venta(empresa_id, int(cliente_id), int(venta_id))
    if not v:
        return None, "not_found"

    detalles = list_venta_detalles(empresa_id, int(v.venta_id))
    envio = get_envio(empresa_id, int(v.venta_id))

    return {
        "venta": _venta_dict(v),
        "detalles": [_detalle_dict(d) for d in detalles],
        "envio": _envio_dict(envio),
    }, None
