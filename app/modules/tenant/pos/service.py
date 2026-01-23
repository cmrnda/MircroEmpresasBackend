from decimal import Decimal
from uuid import uuid4
import secrets
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.security.password import hash_password
from app.modules.tenant.pos.repository import (
    get_client_in_tenant_by_id,
    get_client_in_tenant_by_nit,
    ensure_client_link,
    create_client,
    lock_products_for_update,
    create_sale,
    add_sale_detail,
    set_sale_total,
    get_sale_details,
)
from app.modules.notifications.service import NotificationsService


def _dec(v):
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _gen_email(empresa_id: int, nit_ci: str | None):
    base = (nit_ci or "anon").strip() or "anon"
    u = uuid4().hex
    return f"pos.{int(empresa_id)}.{base}.{u}@local.invalid"


def _gen_password():
    return secrets.token_urlsafe(24)


def pos_lookup_client(empresa_id: int, nit_ci: str | None):
    nit = (nit_ci or "").strip()
    if not nit:
        return None
    c = get_client_in_tenant_by_nit(empresa_id, nit)
    return c.to_dict() if c else None


def pos_create_client(empresa_id: int, payload: dict):
    nombre = (payload.get("nombre_razon") or "").strip()
    if not nombre:
        return None, "invalid_payload"

    nit = (payload.get("nit_ci") or "").strip() or None
    telefono = (payload.get("telefono") or "").strip() or None
    email = (payload.get("email") or "").strip() or None

    try:
        if nit:
            existing = get_client_in_tenant_by_nit(empresa_id, nit)
            if existing:
                return existing.to_dict(), None

        if not email:
            email = _gen_email(empresa_id, nit)

        pw_hash = hash_password(_gen_password())

        c = create_client(
            email=email,
            password_hash=pw_hash,
            nombre_razon=nombre,
            nit_ci=nit,
            telefono=telefono,
        )
        ensure_client_link(empresa_id, c.cliente_id)
        db.session.commit()
        return c.to_dict(), None

    except IntegrityError:
        db.session.rollback()
        return None, "email_taken"
    except Exception:
        db.session.rollback()
        return None, "server_error"


def _resolve_or_create_client(empresa_id: int, cliente_payload: dict):
    if not isinstance(cliente_payload, dict):
        return None, "invalid_payload"

    if cliente_payload.get("cliente_id") is not None:
        c = get_client_in_tenant_by_id(empresa_id, int(cliente_payload.get("cliente_id")))
        if not c:
            return None, "invalid_cliente"
        return c, None

    nit = (cliente_payload.get("nit_ci") or "").strip() or None
    if nit:
        c = get_client_in_tenant_by_nit(empresa_id, nit)
        if c:
            return c, None

    nombre = (cliente_payload.get("nombre_razon") or "").strip()
    if not nombre:
        return None, "cliente_not_found"

    data, err = pos_create_client(
        empresa_id,
        {
            "nit_ci": nit,
            "nombre_razon": nombre,
            "telefono": cliente_payload.get("telefono"),
            "email": cliente_payload.get("email"),
        },
    )
    if err:
        return None, err

    c2 = get_client_in_tenant_by_id(empresa_id, int(data.get("cliente_id")))
    if not c2:
        return None, "server_error"
    return c2, None


def pos_create_sale(empresa_id: int, payload: dict):
    items = payload.get("items") or []
    if not isinstance(items, list) or len(items) == 0:
        return None, "invalid_payload"

    producto_ids = []
    for it in items:
        if it.get("producto_id") is None or it.get("cantidad") is None:
            return None, "invalid_payload"
        producto_ids.append(int(it.get("producto_id")))

    try:
        c, err = _resolve_or_create_client(empresa_id, payload.get("cliente") or {})
        if err:
            return None, err

        products = lock_products_for_update(empresa_id, producto_ids)
        by_id = {int(p.producto_id): p for p in products}

        for it in items:
            pid = int(it.get("producto_id"))
            if pid not in by_id:
                return None, "invalid_producto"
            p = by_id[pid]
            if not bool(getattr(p, "activo", True)):
                return None, "invalid_producto"
            qty = _dec(it.get("cantidad"))
            if qty <= 0:
                return None, "invalid_payload"
            if _dec(getattr(p, "stock", 0)) < qty:
                return None, "stock_insuficiente"

        v = create_sale(empresa_id, int(c.cliente_id), payload)

        total = Decimal("0")
        for it in items:
            pid = int(it.get("producto_id"))
            p = by_id[pid]
            qty = _dec(it.get("cantidad"))

            precio = _dec(it.get("precio_unit")) if it.get("precio_unit") is not None else _dec(getattr(p, "precio", 0))
            desc = _dec(it.get("descuento") or 0)
            if desc < 0:
                return None, "invalid_payload"

            subtotal = (qty * precio) - desc
            if subtotal < 0:
                subtotal = Decimal("0")

            add_sale_detail(empresa_id, v.venta_id, it, precio, subtotal)
            total += subtotal

            prev_stock = _dec(getattr(p, "stock", 0))
            new_stock = prev_stock - qty
            p.stock = new_stock
            db.session.add(p)

            if NotificationsService.should_fire_stock_zero(prev_stock, new_stock):
                NotificationsService.notify_stock_zero(
                    empresa_id=int(empresa_id),
                    producto_id=int(p.producto_id),
                    codigo=getattr(p, "codigo", None),
                    descripcion=getattr(p, "descripcion", None),
                )
            else:
                stock_min = getattr(p, "stock_min", 0)
                if NotificationsService.should_fire_stock_min(prev_stock, stock_min, new_stock):
                    NotificationsService.notify_stock_min(
                        empresa_id=int(empresa_id),
                        producto_id=int(p.producto_id),
                        codigo=getattr(p, "codigo", None),
                        descripcion=getattr(p, "descripcion", None),
                        stock=new_stock,
                        stock_min=stock_min,
                    )

        descuento_total = _dec(payload.get("descuento_total") or 0)
        if descuento_total < 0:
            return None, "invalid_payload"

        total = total - descuento_total
        if total < 0:
            total = Decimal("0")

        set_sale_total(v, total)

        db.session.commit()

        det = get_sale_details(empresa_id, v.venta_id)
        return {
            "venta": v.to_dict(),
            "cliente": c.to_dict(),
            "detalle": [d.to_dict() for d in det],
        }, None

    except IntegrityError:
        db.session.rollback()
        return None, "conflict"
    except Exception:
        db.session.rollback()
        return None, "server_error"
