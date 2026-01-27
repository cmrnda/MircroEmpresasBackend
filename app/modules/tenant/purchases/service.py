from __future__ import annotations

from datetime import date
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.tenant.purchases.repository import (
    supplier_exists,
    product_exists,
    list_purchases,
    get_purchase,
    get_purchase_for_update,
    list_purchase_details,
    get_purchase_detail_for_update,
    create_purchase,
    add_purchase_detail,
    update_purchase_detail,
    delete_purchase_detail,
    recompute_total,
    apply_stock_increase,
    mark_received,
    mark_canceled,
    upsert_proveedor_producto,
)


def _parse_date(s) -> date | None:
    if s is None:
        return None
    val = str(s).strip()
    if not val:
        return None
    return date.fromisoformat(val)


def tenant_list_purchases(empresa_id: int, proveedor_id=None, estado=None):
    return list_purchases(int(empresa_id), proveedor_id=proveedor_id, estado=estado)


def tenant_get_purchase(empresa_id: int, compra_id: int):
    c = get_purchase(int(empresa_id), int(compra_id))
    if not c:
        return None
    det = list_purchase_details(int(empresa_id), int(compra_id))
    c["detalle"] = det
    return c


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
                lote = it.get("lote")
                fecha_vencimiento = it.get("fecha_vencimiento")

                if pid is None or cantidad is None or costo_unit is None:
                    raise ValueError("invalid_item")

                try:
                    pid = int(pid)
                except (TypeError, ValueError):
                    raise ValueError("invalid_item")

                if not product_exists(empresa_id, pid):
                    raise ValueError("invalid_producto")

                fv = _parse_date(fecha_vencimiento)
                add_purchase_detail(
                    empresa_id,
                    compra_id,
                    pid,
                    cantidad,
                    costo_unit,
                    lote=lote,
                    fecha_vencimiento=fv,
                )

                upsert_proveedor_producto(empresa_id, proveedor_id, pid)

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


def tenant_add_purchase_item(empresa_id: int, compra_id: int, payload: dict):
    empresa_id = int(empresa_id)
    compra_id = int(compra_id)

    try:
        with db.session.begin():
            c = get_purchase_for_update(empresa_id, compra_id)
            if not c:
                raise ValueError("not_found")
            if c.estado != "CREADA":
                raise ValueError("invalid_state")

            pid = payload.get("producto_id")
            cantidad = payload.get("cantidad")
            costo_unit = payload.get("costo_unit")
            lote = payload.get("lote")
            fecha_vencimiento = payload.get("fecha_vencimiento")

            if pid is None or cantidad is None or costo_unit is None:
                raise ValueError("invalid_item")

            try:
                pid = int(pid)
            except (TypeError, ValueError):
                raise ValueError("invalid_item")

            if not product_exists(empresa_id, pid):
                raise ValueError("invalid_producto")

            fv = _parse_date(fecha_vencimiento)
            add_purchase_detail(
                empresa_id,
                compra_id,
                pid,
                cantidad,
                costo_unit,
                lote=lote,
                fecha_vencimiento=fv,
            )

            upsert_proveedor_producto(empresa_id, int(c.proveedor_id), pid)

            recompute_total(empresa_id, compra_id)

        return tenant_get_purchase(empresa_id, compra_id), None

    except ValueError as e:
        db.session.rollback()
        if str(e) == "not_found":
            return None, "not_found"
        if str(e) == "invalid_state":
            return None, "invalid_state"
        if str(e) == "invalid_producto":
            return None, "invalid_producto"
        return None, "invalid_payload"
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"


def tenant_update_purchase_item(empresa_id: int, compra_id: int, compra_detalle_id: int, payload: dict):
    empresa_id = int(empresa_id)
    compra_id = int(compra_id)
    compra_detalle_id = int(compra_detalle_id)

    try:
        with db.session.begin():
            c = get_purchase_for_update(empresa_id, compra_id)
            if not c:
                raise ValueError("not_found")
            if c.estado != "CREADA":
                raise ValueError("invalid_state")

            d = get_purchase_detail_for_update(empresa_id, compra_id, compra_detalle_id)
            if not d:
                raise ValueError("not_found_item")

            cantidad = payload.get("cantidad", None)
            costo_unit = payload.get("costo_unit", None)
            lote = payload.get("lote", None) if "lote" in payload else None
            fv = _parse_date(payload.get("fecha_vencimiento", None)) if "fecha_vencimiento" in payload else None

            update_purchase_detail(d, cantidad=cantidad, costo_unit=costo_unit, lote=lote, fecha_vencimiento=fv)
            recompute_total(empresa_id, compra_id)

        return tenant_get_purchase(empresa_id, compra_id), None

    except ValueError as e:
        db.session.rollback()
        if str(e) == "not_found":
            return None, "not_found"
        if str(e) == "not_found_item":
            return None, "not_found_item"
        if str(e) == "invalid_state":
            return None, "invalid_state"
        return None, "invalid_payload"
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"


def tenant_delete_purchase_item(empresa_id: int, compra_id: int, compra_detalle_id: int):
    empresa_id = int(empresa_id)
    compra_id = int(compra_id)
    compra_detalle_id = int(compra_detalle_id)

    try:
        with db.session.begin():
            c = get_purchase_for_update(empresa_id, compra_id)
            if not c:
                raise ValueError("not_found")
            if c.estado != "CREADA":
                raise ValueError("invalid_state")

            d = get_purchase_detail_for_update(empresa_id, compra_id, compra_detalle_id)
            if not d:
                raise ValueError("not_found_item")

            delete_purchase_detail(d)
            recompute_total(empresa_id, compra_id)

        return tenant_get_purchase(empresa_id, compra_id), None

    except ValueError as e:
        db.session.rollback()
        if str(e) == "not_found":
            return None, "not_found"
        if str(e) == "not_found_item":
            return None, "not_found_item"
        return None, "invalid_state"


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
