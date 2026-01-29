from __future__ import annotations

from datetime import datetime, date, time, timedelta, timezone
from decimal import Decimal

from app.extensions import db
from app.database.models.compra import Compra
from app.database.models.compra_detalle import CompraDetalle
from app.database.models.proveedor import Proveedor
from app.database.models.venta import Venta, VentaDetalle
from app.database.models.producto import Producto
from app.database.models.categoria import Categoria
from app.database.models.cliente import Cliente, ClienteEmpresa


def tenant_dashboard(
        empresa_id: int,
        date_from: str | None,
        date_to: str | None,
        group: str | None,
        limit: int,
) -> dict:
    eid = int(empresa_id)
    g = (group or "day").strip().lower()
    if g not in ("day", "month"):
        g = "day"

    lim = int(limit or 10)
    if lim <= 0:
        lim = 10
    if lim > 50:
        lim = 50

    start, end_excl = _dt_range(date_from, date_to)

    expenses_total, purchases_count = _expenses_total_and_count(eid, start, end_excl)
    revenue_total, sales_count = _revenue_total_and_count(eid, start, end_excl)

    profit_total = revenue_total - expenses_total
    profit_margin_pct = Decimal("0")
    if revenue_total > 0:
        profit_margin_pct = (profit_total / revenue_total) * Decimal("100")

    avg_purchase_total = Decimal("0")
    if purchases_count > 0:
        avg_purchase_total = expenses_total / Decimal(str(purchases_count))

    avg_sale_total = Decimal("0")
    if sales_count > 0:
        avg_sale_total = revenue_total / Decimal(str(sales_count))

    products_count = int(
        db.session.query(db.func.count(Producto.producto_id))
        .filter(Producto.empresa_id == eid)
        .filter(Producto.activo.is_(True))
        .scalar()
        or 0
    )

    categories_count = int(
        db.session.query(db.func.count(Categoria.categoria_id))
        .filter(Categoria.empresa_id == eid)
        .filter(Categoria.activo.is_(True))
        .scalar()
        or 0
    )

    suppliers_count = int(
        db.session.query(db.func.count(Proveedor.proveedor_id))
        .filter(Proveedor.empresa_id == eid)
        .filter(Proveedor.activo.is_(True))
        .scalar()
        or 0
    )

    clients_count = int(
        db.session.query(db.func.count(ClienteEmpresa.cliente_id))
        .filter(ClienteEmpresa.empresa_id == eid)
        .filter(ClienteEmpresa.activo.is_(True))
        .scalar()
        or 0
    )

    low_stock_count = int(
        db.session.query(db.func.count(Producto.producto_id))
        .filter(Producto.empresa_id == eid)
        .filter(Producto.activo.is_(True))
        .filter(Producto.stock <= Producto.stock_min)
        .scalar()
        or 0
    )

    overview = {
        "revenue_total": float(revenue_total),
        "expenses_total": float(expenses_total),
        "profit_total": float(profit_total),
        "profit_margin_pct": float(profit_margin_pct),
        "sales_count": int(sales_count),
        "purchases_count": int(purchases_count),
        "avg_sale_total": float(avg_sale_total),
        "avg_purchase_total": float(avg_purchase_total),
        "products_count": products_count,
        "categories_count": categories_count,
        "suppliers_count": suppliers_count,
        "clients_count": clients_count,
        "low_stock_count": low_stock_count,
    }

    series = {
        "revenue": _revenue_series(eid, start, end_excl, g),
        "expenses": _expenses_series(eid, start, end_excl, g),
    }

    suppliers = {"items": _suppliers_summary(eid, start, end_excl, lim)}
    top_products = {"items": _top_products(eid, start, end_excl, lim)}
    top_categories = {"items": _top_categories(eid, start, end_excl, lim)}

    inv_valuation = _inventory_valuation(eid)
    inv_alerts = {"items": _inventory_alerts(eid, lim)}

    recent_sales = {"items": _recent_sales(eid, lim)}
    recent_purchases = {"items": _recent_purchases(eid, lim)}

    return {
        "empresa_id": eid,
        "from": date_from,
        "to": date_to,
        "group": g,
        "overview": overview,
        "series": {"revenue": series["revenue"], "expenses": series["expenses"]},
        "suppliers": suppliers,
        "top_products": top_products,
        "top_categories": top_categories,
        "inventory": {"valuation": inv_valuation, "alerts": inv_alerts},
        "recent": {"sales": recent_sales, "purchases": recent_purchases},
    }


def tenant_dashboard_sale_detail(empresa_id: int, venta_id: int) -> dict | None:
    v = (
        db.session.query(Venta)
        .filter(Venta.empresa_id == int(empresa_id))
        .filter(Venta.venta_id == int(venta_id))
        .first()
    )
    if not v:
        return None

    details = (
        db.session.query(VentaDetalle, Producto.codigo, Producto.descripcion)
        .outerjoin(
            Producto,
            (Producto.empresa_id == VentaDetalle.empresa_id) & (Producto.producto_id == VentaDetalle.producto_id),
            )
        .filter(VentaDetalle.empresa_id == int(empresa_id))
        .filter(VentaDetalle.venta_id == int(venta_id))
        .order_by(VentaDetalle.venta_detalle_id.asc())
        .all()
    )

    items = []
    for d, codigo, descripcion in details:
        x = d.to_dict()
        x["producto_codigo"] = codigo
        x["producto_descripcion"] = descripcion
        items.append(x)

    return {"empresa_id": int(empresa_id), "venta": v.to_dict(), "items": items}


def tenant_dashboard_purchase_detail(empresa_id: int, compra_id: int) -> dict | None:
    c = (
        db.session.query(Compra)
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.compra_id == int(compra_id))
        .first()
    )
    if not c:
        return None

    details = (
        db.session.query(CompraDetalle)
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(CompraDetalle.compra_id == int(compra_id))
        .order_by(CompraDetalle.compra_detalle_id.asc())
        .all()
    )

    return {"empresa_id": int(empresa_id), "compra": c.to_dict(), "items": [d.to_dict() for d in details]}


def _expenses_total_and_count(empresa_id: int, start, end_excl) -> tuple[Decimal, int]:
    q = (
        db.session.query(
            db.func.coalesce(db.func.sum(Compra.total), 0).label("total"),
            db.func.count(Compra.compra_id).label("n"),
        )
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.estado == "RECIBIDA")
    )
    if start is not None:
        q = q.filter(Compra.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Compra.fecha_hora < end_excl)

    total, n = q.first() or (0, 0)
    return _dec(total), int(n or 0)


def _revenue_total_and_count(empresa_id: int, start, end_excl) -> tuple[Decimal, int]:
    q = (
        db.session.query(
            db.func.coalesce(db.func.sum(Venta.total), 0).label("total"),
            db.func.count(Venta.venta_id).label("n"),
        )
        .filter(Venta.empresa_id == int(empresa_id))
    )
    if start is not None:
        q = q.filter(Venta.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Venta.fecha_hora < end_excl)

    total, n = q.first() or (0, 0)
    return _dec(total), int(n or 0)


def _revenue_series(empresa_id: int, start, end_excl, group: str) -> list[dict]:
    if group == "month":
        period_expr = db.func.date_trunc("month", Venta.fecha_hora)
    else:
        period_expr = db.func.date(Venta.fecha_hora)

    q = (
        db.session.query(
            period_expr.label("periodo"),
            db.func.coalesce(db.func.sum(Venta.total), 0).label("total"),
        )
        .filter(Venta.empresa_id == int(empresa_id))
    )
    if start is not None:
        q = q.filter(Venta.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Venta.fecha_hora < end_excl)

    q = q.group_by("periodo").order_by("periodo")

    items = []
    for periodo, total in q.all():
        if isinstance(periodo, datetime):
            label = periodo.date().isoformat()
        else:
            label = str(periodo)
        items.append({"periodo": label, "total": float(_dec(total))})
    return items


def _expenses_series(empresa_id: int, start, end_excl, group: str) -> list[dict]:
    if group == "month":
        period_expr = db.func.date_trunc("month", Compra.fecha_hora)
    else:
        period_expr = db.func.date(Compra.fecha_hora)

    q = (
        db.session.query(
            period_expr.label("periodo"),
            db.func.coalesce(db.func.sum(Compra.total), 0).label("total"),
        )
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.estado == "RECIBIDA")
    )
    if start is not None:
        q = q.filter(Compra.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Compra.fecha_hora < end_excl)

    q = q.group_by("periodo").order_by("periodo")

    items = []
    for periodo, total in q.all():
        if isinstance(periodo, datetime):
            label = periodo.date().isoformat()
        else:
            label = str(periodo)
        items.append({"periodo": label, "total": float(_dec(total))})
    return items


def _suppliers_summary(empresa_id: int, start, end_excl, limit: int) -> list[dict]:
    base = (
        db.session.query(
            Compra.proveedor_id.label("proveedor_id"),
            db.func.coalesce(db.func.sum(Compra.total), 0).label("compras_total"),
            db.func.count(Compra.compra_id).label("n_compras"),
            db.func.max(Compra.fecha_hora).label("ultima_fecha"),
        )
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.estado == "RECIBIDA")
    )
    if start is not None:
        base = base.filter(Compra.fecha_hora >= start)
    if end_excl is not None:
        base = base.filter(Compra.fecha_hora < end_excl)

    rows = (
        base.group_by(Compra.proveedor_id)
        .order_by(db.desc("compras_total"))
        .limit(int(limit))
        .offset(0)
        .all()
    )

    items = []
    for proveedor_id, compras_total, n_compras, ultima_fecha in rows:
        p = (
            db.session.query(Proveedor)
            .filter(Proveedor.empresa_id == int(empresa_id))
            .filter(Proveedor.proveedor_id == int(proveedor_id))
            .first()
        )
        items.append(
            {
                "proveedor_id": int(proveedor_id),
                "proveedor_nombre": (p.nombre if p else None),
                "compras_total": float(_dec(compras_total)),
                "n_compras": int(n_compras or 0),
                "ultima_compra_fecha": ultima_fecha.isoformat() if ultima_fecha else None,
            }
        )
    return items


def _top_products(empresa_id: int, start, end_excl, limit: int) -> list[dict]:
    q = (
        db.session.query(
            Producto.producto_id,
            Producto.codigo,
            Producto.descripcion,
            db.func.coalesce(db.func.sum(VentaDetalle.cantidad), 0).label("qty"),
            db.func.coalesce(db.func.sum(VentaDetalle.subtotal), 0).label("total"),
        )
        .join(
            VentaDetalle,
            (VentaDetalle.empresa_id == Producto.empresa_id) & (VentaDetalle.producto_id == Producto.producto_id),
            )
        .join(
            Venta,
            (Venta.empresa_id == VentaDetalle.empresa_id) & (Venta.venta_id == VentaDetalle.venta_id),
            )
        .filter(Producto.empresa_id == int(empresa_id))
    )
    if start is not None:
        q = q.filter(Venta.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Venta.fecha_hora < end_excl)

    q = (
        q.group_by(Producto.producto_id, Producto.codigo, Producto.descripcion)
        .order_by(db.desc("total"))
        .limit(int(limit))
        .offset(0)
    )

    items = []
    for producto_id, codigo, descripcion, qty, total in q.all():
        items.append(
            {
                "producto_id": int(producto_id),
                "codigo": str(codigo),
                "descripcion": str(descripcion),
                "qty": float(_dec(qty)),
                "total": float(_dec(total)),
            }
        )
    return items


def _top_categories(empresa_id: int, start, end_excl, limit: int) -> list[dict]:
    q = (
        db.session.query(
            Categoria.categoria_id,
            Categoria.nombre,
            db.func.coalesce(db.func.sum(VentaDetalle.subtotal), 0).label("total"),
        )
        .join(
            Producto,
            (Producto.empresa_id == Categoria.empresa_id) & (Producto.categoria_id == Categoria.categoria_id),
            )
        .join(
            VentaDetalle,
            (VentaDetalle.empresa_id == Producto.empresa_id) & (VentaDetalle.producto_id == Producto.producto_id),
            )
        .join(
            Venta,
            (Venta.empresa_id == VentaDetalle.empresa_id) & (Venta.venta_id == VentaDetalle.venta_id),
            )
        .filter(Categoria.empresa_id == int(empresa_id))
    )
    if start is not None:
        q = q.filter(Venta.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Venta.fecha_hora < end_excl)

    q = (
        q.group_by(Categoria.categoria_id, Categoria.nombre)
        .order_by(db.desc("total"))
        .limit(int(limit))
        .offset(0)
    )

    items = []
    for categoria_id, nombre, total in q.all():
        items.append(
            {
                "categoria_id": int(categoria_id),
                "categoria_nombre": str(nombre),
                "total": float(_dec(total)),
            }
        )
    return items


def _inventory_alerts(empresa_id: int, limit: int) -> list[dict]:
    q = (
        db.session.query(
            Producto.producto_id,
            Producto.codigo,
            Producto.descripcion,
            Producto.stock,
            Producto.stock_min,
            Categoria.nombre.label("categoria_nombre"),
        )
        .outerjoin(
            Categoria,
            (Categoria.empresa_id == Producto.empresa_id) & (Categoria.categoria_id == Producto.categoria_id),
            )
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.activo.is_(True))
        .filter(Producto.stock <= Producto.stock_min)
        .order_by(Producto.stock.asc(), Producto.producto_id.asc())
        .limit(int(limit))
        .offset(0)
    )

    items = []
    for producto_id, codigo, descripcion, stock, stock_min, categoria_nombre in q.all():
        items.append(
            {
                "producto_id": int(producto_id),
                "codigo": str(codigo),
                "descripcion": str(descripcion),
                "categoria_nombre": categoria_nombre,
                "stock": float(_dec(stock)),
                "stock_min": int(stock_min or 0),
            }
        )
    return items


def _inventory_valuation(empresa_id: int) -> dict:
    price_total = (
            db.session.query(db.func.coalesce(db.func.sum(Producto.stock * Producto.precio), 0))
            .filter(Producto.empresa_id == int(empresa_id))
            .scalar()
            or 0
    )

    sub_cost = (
        db.session.query(
            CompraDetalle.producto_id.label("producto_id"),
            (db.func.sum(CompraDetalle.cantidad * CompraDetalle.costo_unit) / db.func.nullif(db.func.sum(CompraDetalle.cantidad), 0)).label(
                "avg_cost"
            ),
        )
        .join(
            Compra,
            (Compra.empresa_id == CompraDetalle.empresa_id) & (Compra.compra_id == CompraDetalle.compra_id),
            )
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(Compra.estado == "RECIBIDA")
        .group_by(CompraDetalle.producto_id)
        .subquery()
    )

    cost_total = (
            db.session.query(db.func.coalesce(db.func.sum(Producto.stock * db.func.coalesce(sub_cost.c.avg_cost, 0)), 0))
            .outerjoin(sub_cost, sub_cost.c.producto_id == Producto.producto_id)
            .filter(Producto.empresa_id == int(empresa_id))
            .scalar()
            or 0
    )

    return {
        "inventory_price_value": float(_dec(price_total)),
        "inventory_avg_cost_value": float(_dec(cost_total)),
    }


def _recent_purchases(empresa_id: int, limit: int) -> list[dict]:
    q = (
        db.session.query(Compra, Proveedor.nombre)
        .outerjoin(
            Proveedor,
            (Proveedor.empresa_id == Compra.empresa_id) & (Proveedor.proveedor_id == Compra.proveedor_id),
            )
        .filter(Compra.empresa_id == int(empresa_id))
        .order_by(Compra.fecha_hora.desc(), Compra.compra_id.desc())
        .limit(int(limit))
        .offset(0)
    )

    items = []
    for c, proveedor_nombre in q.all():
        d = c.to_dict()
        d["proveedor_nombre"] = proveedor_nombre
        items.append(d)
    return items


def _recent_sales(empresa_id: int, limit: int) -> list[dict]:
    q = (
        db.session.query(Venta, Cliente.nombre_razon)
        .outerjoin(
            ClienteEmpresa,
            (ClienteEmpresa.empresa_id == Venta.empresa_id) & (ClienteEmpresa.cliente_id == Venta.cliente_id),
            )
        .outerjoin(Cliente, Cliente.cliente_id == ClienteEmpresa.cliente_id)
        .filter(Venta.empresa_id == int(empresa_id))
        .order_by(Venta.fecha_hora.desc(), Venta.venta_id.desc())
        .limit(int(limit))
        .offset(0)
    )

    items = []
    for v, cliente_nombre in q.all():
        d = v.to_dict()
        d["cliente_nombre"] = cliente_nombre
        items.append(d)
    return items


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _parse_ymd(s: str | None) -> date | None:
    s = (s or "").strip()
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d").date()


def _dt_range(from_ymd: str | None, to_ymd: str | None):
    d_from = _parse_ymd(from_ymd)
    d_to = _parse_ymd(to_ymd)

    start = None
    end_excl = None

    if d_from:
        start = datetime.combine(d_from, time.min).replace(tzinfo=timezone.utc)
    if d_to:
        end_excl = datetime.combine(d_to + timedelta(days=1), time.min).replace(tzinfo=timezone.utc)

    return start, end_excl
