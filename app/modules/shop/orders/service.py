from decimal import Decimal
from app.extensions import db
from app.modules.shop.orders.repository import (
    cliente_in_tenant,
    lock_products_for_update,
    create_order,
    add_detail,
    set_order_total,
    notify_tenant_new_order,
    # notify_client_created,
    list_client_orders,
    get_client_order,
    get_details,
)

def _dec(v):
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")

def shop_create_order(empresa_id: int, cliente_id: int, payload: dict):
    items = payload.get("items") or []
    if not isinstance(items, list) or len(items) == 0:
        return None, "invalid_payload"

    if not cliente_in_tenant(empresa_id, cliente_id):
        return None, "forbidden"

    producto_ids = []
    for it in items:
        if it.get("producto_id") is None or it.get("cantidad") is None:
            return None, "invalid_payload"
        producto_ids.append(int(it.get("producto_id")))

    try:
        products = lock_products_for_update(empresa_id, producto_ids)
        by_id = {int(p.producto_id): p for p in products}

        for it in items:
            pid = int(it.get("producto_id"))
            if pid not in by_id:
                db.session.rollback()
                return None, "invalid_producto"

            p = by_id[pid]
            if not bool(p.activo):
                db.session.rollback()
                return None, "invalid_producto"

            qty = _dec(it.get("cantidad"))
            if qty <= 0:
                db.session.rollback()
                return None, "invalid_payload"

            if _dec(p.stock) < qty:
                db.session.rollback()
                return None, "stock_insuficiente"

        v = create_order(empresa_id, cliente_id, payload)

        total = Decimal("0")
        for it in items:
            pid = int(it.get("producto_id"))
            p = by_id[pid]

            qty = _dec(it.get("cantidad"))
            precio = _dec(it.get("precio_unit")) if it.get("precio_unit") is not None else _dec(p.precio)
            desc = _dec(it.get("descuento") or 0)

            if desc < 0:
                db.session.rollback()
                return None, "invalid_payload"

            subtotal = (qty * precio) - desc
            if subtotal < 0:
                subtotal = Decimal("0")

            add_detail(empresa_id, v.venta_id, it, precio, subtotal)

            total += subtotal
            p.stock = _dec(p.stock) - qty
            db.session.add(p)

        envio_costo = _dec(payload.get("envio_costo") or 0)
        descuento_total = _dec(payload.get("descuento_total") or 0)
        if envio_costo < 0 or descuento_total < 0:
            db.session.rollback()
            return None, "invalid_payload"

        total = total + envio_costo - descuento_total
        if total < 0:
            total = Decimal("0")

        set_order_total(v, total)
        notify_tenant_new_order(empresa_id, v.venta_id)
        # notify_client_created(empresa_id, cliente_id, v.venta_id)

        db.session.commit()

        data = v.to_dict()
        det = get_details(empresa_id, v.venta_id)
        data["detalle"] = [d.to_dict() for d in det]
        return data, None

    except Exception:
        db.session.rollback()
        return None, "order_failed"

def shop_list_my_orders(empresa_id: int, cliente_id: int):
    rows = list_client_orders(empresa_id, cliente_id)
    return [v.to_dict() for v in rows]

def shop_get_my_order(empresa_id: int, cliente_id: int, venta_id: int):
    v = get_client_order(empresa_id, cliente_id, venta_id)
    if not v:
        return None
    det = get_details(empresa_id, venta_id)
    data = v.to_dict()
    data["detalle"] = [d.to_dict() for d in det]
    return data
