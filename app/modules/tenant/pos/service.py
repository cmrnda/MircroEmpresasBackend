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

from app.modules.tenant.pos.pdf import build_sale_receipt_pdf
# app/modules/tenant/pos/service.py
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from . import repository as repo

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
def tenant_get_sale_receipt_pdf(empresa_id: int, venta_id: int):
    try:
        pdf_bytes = build_sale_receipt_pdf(int(empresa_id), int(venta_id))
        return pdf_bytes, None
    except ValueError:
        return None, "not_found"
    except Exception:
        return None, "pdf_failed"
    
def _money(x: Any) -> str:
    try:
        return f"{float(x or 0):.2f}"
    except Exception:
        return "0.00"


def _dt(s: Any) -> str:
    if not s:
        return "-"
    try:
        # si ya viene como datetime, ok
        if isinstance(s, datetime):
            return s.strftime("%Y-%m-%d %H:%M")
        # si viene string tipo ISO
        return str(s).replace("T", " ")[:16]
    except Exception:
        return str(s)


def tenant_generate_sale_receipt_pdf(empresa_id: int, venta_id: int) -> Tuple[Optional[bytes], Optional[str]]:
    data = repo.get_sale_receipt_data(int(empresa_id), int(venta_id))
    if not data:
        return None, "not_found"

    header = data["header"]
    items = data["items"]

    # ---- PDF ----
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    x0 = 18 * mm
    y = h - 18 * mm

    # Encabezado empresa
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x0, y, str(header.get("empresa_nombre") or "EMPRESA"))
    y -= 6 * mm

    c.setFont("Helvetica", 9)
    c.drawString(x0, y, f"NIT: {header.get('empresa_nit') or '-'}")
    y -= 4.5 * mm
    c.drawString(x0, y, f"Dirección: {header.get('empresa_direccion') or '-'}")
    y -= 4.5 * mm
    c.drawString(x0, y, f"Tel: {header.get('empresa_telefono') or '-'}")
    y -= 6 * mm

    c.setLineWidth(0.7)
    c.line(x0, y, w - x0, y)
    y -= 6 * mm

    # Datos de recibo/venta
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x0, y, "RECIBO / COMPROBANTE DE VENTA")
    y -= 6 * mm

    c.setFont("Helvetica", 9)
    c.drawString(x0, y, f"Venta #: {header.get('venta_id')}")
    c.drawRightString(w - x0, y, f"Fecha: {_dt(header.get('fecha_hora'))}")
    y -= 4.5 * mm

    c.drawString(x0, y, f"Estado: {header.get('estado') or '-'}")
    c.drawRightString(w - x0, y, f"Empresa #: {header.get('empresa_id')}")
    y -= 7 * mm

    # Cliente
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y, "Cliente")
    y -= 5 * mm

    c.setFont("Helvetica", 9)
    c.drawString(x0, y, f"Nombre/Razón: {header.get('cliente_nombre') or '-'}")
    y -= 4.5 * mm
    c.drawString(x0, y, f"NIT/CI: {header.get('cliente_nit_ci') or '-'}")
    y -= 4.5 * mm
    c.drawString(x0, y, f"Tel: {header.get('cliente_telefono') or '-'}   Email: {header.get('cliente_email') or '-'}")
    y -= 7 * mm

    c.setLineWidth(0.7)
    c.line(x0, y, w - x0, y)
    y -= 6 * mm

    # Tabla items (simple)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x0, y, "Detalle")
    y -= 5 * mm

    # headers
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(x0, y, "Producto")
    c.drawRightString(w - x0 - 90, y, "Cant.")
    c.drawRightString(w - x0 - 55, y, "P.Unit")
    c.drawRightString(w - x0, y, "Subtotal")
    y -= 4 * mm

    c.setLineWidth(0.3)
    c.line(x0, y, w - x0, y)
    y -= 4.5 * mm

    c.setFont("Helvetica", 8.5)

    for it in items:
        # salto de página si se acaba
        if y < 40 * mm:
            c.showPage()
            y = h - 18 * mm
            c.setFont("Helvetica", 8.5)

        desc = str(it.get("producto_descripcion") or it.get("producto_codigo") or "Item")
        # recorta para que no rompa todo
        if len(desc) > 46:
            desc = desc[:46] + "…"

        c.drawString(x0, y, desc)
        c.drawRightString(w - x0 - 90, y, str(it.get("cantidad") or 0))
        c.drawRightString(w - x0 - 55, y, _money(it.get("precio_unit")))
        c.drawRightString(w - x0, y, _money(it.get("subtotal")))
        y -= 5 * mm

    y -= 3 * mm
    c.setLineWidth(0.7)
    c.line(x0, y, w - x0, y)
    y -= 7 * mm

    # Totales
    c.setFont("Helvetica", 9)
    c.drawRightString(w - x0 - 55, y, "Descuento:")
    c.drawRightString(w - x0, y, _money(header.get("descuento_total")))
    y -= 5 * mm

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(w - x0 - 55, y, "TOTAL:")
    c.drawRightString(w - x0, y, _money(header.get("total")))
    y -= 7 * mm

    # Pago
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y, "Pago")
    y -= 5 * mm

    c.setFont("Helvetica", 9)
    c.drawString(x0, y, f"Método: {header.get('pago_metodo') or '-'}")
    y -= 4.5 * mm
    c.drawString(x0, y, f"Monto: {_money(header.get('pago_monto'))}")
    y -= 4.5 * mm
    c.drawString(x0, y, f"Estado: {header.get('pago_estado') or '-'}")
    y -= 4.5 * mm
    c.drawString(x0, y, f"Pagado en: {_dt(header.get('pagado_en'))}")
    y -= 4.5 * mm

    ref = header.get("pago_referencia_qr")
    if ref:
        c.drawString(x0, y, f"Ref/QR: {ref}")
        y -= 4.5 * mm

    # Footer
    y = max(y, 20 * mm)
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(w / 2, 12 * mm, "Gracias por su compra.")

    c.showPage()
    c.save()

    pdf = buf.getvalue()
    buf.close()
    return pdf, None