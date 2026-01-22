# app/modules/tenant/purchases/service.py

from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.tenant.purchases.repository import (
    supplier_exists,
    product_exists,
    list_purchases,
    get_purchase,
    get_purchase_for_update,
    list_purchase_details,
    create_purchase,
    add_purchase_detail,
    recompute_total,
    apply_stock_increase,
    mark_received,
    mark_canceled,
)

def tenant_list_purchases(empresa_id: int, proveedor_id=None, estado=None):
    rows = list_purchases(int(empresa_id), proveedor_id=proveedor_id, estado=estado)
    return [r.to_dict() for r in rows]

def tenant_get_purchase(empresa_id: int, compra_id: int):
    c = get_purchase(int(empresa_id), int(compra_id))
    if not c:
        return None
    det = list_purchase_details(int(empresa_id), int(compra_id))
    d = c.to_dict()
    d["detalle"] = [x.to_dict() for x in det]
    return d

def tenant_create_purchase(empresa_id: int, payload: dict):
    empresa_id = int(empresa_id)

    proveedor_id = payload.get("proveedor_id")
    detalle = payload.get("detalle")
    observacion = (payload.get("observacion") or "").strip() or None

    if proveedor_id is None:
        return None, "invalid_payload"

    try:
        proveedor_id = int(proveedor_id)
    except (TypeError, ValueError):
        return None, "invalid_payload"

    if not isinstance(detalle, list) or len(detalle) == 0:
        return None, "invalid_detalle"

    compra_id = None

    try:
        with db.session.begin():
            if not supplier_exists(empresa_id, proveedor_id):
                raise ValueError("invalid_proveedor")

            c = create_purchase(empresa_id, proveedor_id, observacion)
            compra_id = int(c.compra_id)

            for it in detalle:
                if not isinstance(it, dict):
                    raise ValueError("invalid_item")

                pid = it.get("producto_id")
                cantidad = it.get("cantidad")
                costo_unit = it.get("costo_unit")

                if pid is None or cantidad is None or costo_unit is None:
                    raise ValueError("invalid_item")

                try:
                    pid = int(pid)
                except (TypeError, ValueError):
                    raise ValueError("invalid_item")

                if not product_exists(empresa_id, pid):
                    raise ValueError("invalid_producto")

                add_purchase_detail(empresa_id, compra_id, pid, cantidad, costo_unit)

            recompute_total(empresa_id, compra_id)

        return tenant_get_purchase(empresa_id, compra_id), None

    except IntegrityError:
        db.session.rollback()
        return None, "conflict"
    except ValueError as e:
        db.session.rollback()
        if str(e) == "invalid_producto":
            return None, "invalid_producto"
        if str(e) == "invalid_detalle":
            return None, "invalid_detalle"
        if str(e) == "invalid_proveedor":
            return None, "invalid_proveedor"
        return None, "invalid_payload"

def tenant_receive_purchase(empresa_id: int, compra_id: int, usuario_id: int):
    empresa_id = int(empresa_id)
    compra_id = int(compra_id)
    usuario_id = int(usuario_id)

    try:
        with db.session.begin():
            c = get_purchase_for_update(empresa_id, compra_id)
            if not c:
                raise ValueError("not_found")
            if c.estado != "CREADA":
                raise ValueError("invalid_state")

            apply_stock_increase(empresa_id, compra_id)
            mark_received(c, usuario_id)

        return tenant_get_purchase(empresa_id, compra_id), None

    except ValueError as e:
        db.session.rollback()
        if str(e) == "not_found":
            return None, "not_found"
        return None, "invalid_state"

def tenant_cancel_purchase(empresa_id: int, compra_id: int):
    empresa_id = int(empresa_id)
    compra_id = int(compra_id)

    try:
        with db.session.begin():
            c = get_purchase_for_update(empresa_id, compra_id)
            if not c:
                raise ValueError("not_found")
            if c.estado != "CREADA":
                raise ValueError("invalid_state")

            mark_canceled(c)

        return tenant_get_purchase(empresa_id, compra_id), None

    except ValueError as e:
        db.session.rollback()
        if str(e) == "not_found":
            return None, "not_found"
        return None, "invalid_state"