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

def tenant_expenses_total(empresa_id: int, date_from: str | None, date_to: str | None) -> dict:
    start, end_excl = _dt_range(date_from, date_to)

    q = (
        db.session.query(db.func.coalesce(db.func.sum(Compra.total), 0))
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.estado == "RECIBIDA")
    )

    if start is not None:
        q = q.filter(Compra.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Compra.fecha_hora < end_excl)

    total = _dec(q.scalar() or 0)

    return {
        "empresa_id": int(empresa_id),
        "compras_total": float(total),
        "from": date_from,
        "to": date_to,
    }


def tenant_expenses_by_supplier(
    empresa_id: int,
    date_from: str | None,
    date_to: str | None,
    limit: int,
    offset: int,
) -> dict:
    start, end_excl = _dt_range(date_from, date_to)

    q = (
        db.session.query(
            Proveedor.proveedor_id,
            Proveedor.nombre,
            db.func.coalesce(db.func.sum(Compra.total), 0).label("total"),
        )
        .join(
            Compra,
            (Compra.empresa_id == Proveedor.empresa_id) & (Compra.proveedor_id == Proveedor.proveedor_id),
        )
        .filter(Proveedor.empresa_id == int(empresa_id))
        .filter(Compra.estado == "RECIBIDA")
    )

    if start is not None:
        q = q.filter(Compra.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Compra.fecha_hora < end_excl)

    q = (
        q.group_by(Proveedor.proveedor_id, Proveedor.nombre)
        .order_by(db.desc("total"))
        .limit(int(limit))
        .offset(int(offset))
    )

    items = []
    for proveedor_id, nombre, total in q.all():
        items.append(
            {
                "proveedor_id": int(proveedor_id),
                "proveedor_nombre": str(nombre),
                "total": float(_dec(total)),
            }
        )

    return {
        "empresa_id": int(empresa_id),
        "from": date_from,
        "to": date_to,
        "limit": int(limit),
        "offset": int(offset),
        "items": items,
    }


def tenant_suppliers_summary(
    empresa_id: int,
    date_from: str | None,
    date_to: str | None,
    limit: int,
    offset: int,
) -> dict:
    """
    Resumen por proveedor: total, n_compras, última compra (fecha y total).
    Solo compras RECIBIDA.
    """
    start, end_excl = _dt_range(date_from, date_to)

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
        .offset(int(offset))
        .all()
    )

    items = []
    for proveedor_id, compras_total, n_compras, ultima_fecha in rows:
        # nombre proveedor
        p = (
            db.session.query(Proveedor)
            .filter(Proveedor.empresa_id == int(empresa_id))
            .filter(Proveedor.proveedor_id == int(proveedor_id))
            .first()
        )

        # última compra total (si hay empates en fecha, toma una)
        last = (
            db.session.query(Compra)
            .filter(Compra.empresa_id == int(empresa_id))
            .filter(Compra.proveedor_id == int(proveedor_id))
            .filter(Compra.estado == "RECIBIDA")
            .order_by(Compra.fecha_hora.desc(), Compra.compra_id.desc())
            .first()
        )

        items.append(
            {
                "proveedor_id": int(proveedor_id),
                "proveedor_nombre": (p.nombre if p else None),
                "compras_total": float(_dec(compras_total)),
                "n_compras": int(n_compras or 0),
                "ultima_compra_fecha": ultima_fecha.isoformat() if ultima_fecha else None,
                "ultima_compra_total": float(_dec(getattr(last, "total", 0))),
            }
        )

    return {
        "empresa_id": int(empresa_id),
        "from": date_from,
        "to": date_to,
        "limit": int(limit),
        "offset": int(offset),
        "items": items,
    }


def tenant_finance_purchases_list(
    empresa_id: int,
    proveedor_id: int | None,
    estado: str | None,
    date_from: str | None,
    date_to: str | None,
    limit: int,
    offset: int,
) -> dict:
    start, end_excl = _dt_range(date_from, date_to)
    est = (estado or "").strip().upper() or None

    q = (
        db.session.query(Compra, Proveedor.nombre)
        .outerjoin(
            Proveedor,
            (Proveedor.empresa_id == Compra.empresa_id) & (Proveedor.proveedor_id == Compra.proveedor_id),
        )
        .filter(Compra.empresa_id == int(empresa_id))
    )

    if proveedor_id:
        q = q.filter(Compra.proveedor_id == int(proveedor_id))
    if est:
        q = q.filter(Compra.estado == est)
    if start is not None:
        q = q.filter(Compra.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Compra.fecha_hora < end_excl)

    q = q.order_by(Compra.fecha_hora.desc(), Compra.compra_id.desc()).limit(int(limit)).offset(int(offset))

    items = []
    for c, proveedor_nombre in q.all():
        d = c.to_dict()
        d["proveedor_nombre"] = proveedor_nombre
        items.append(d)

    return {
        "empresa_id": int(empresa_id),
        "proveedor_id": int(proveedor_id) if proveedor_id else None,
        "estado": est,
        "from": date_from,
        "to": date_to,
        "limit": int(limit),
        "offset": int(offset),
        "items": items,
    }


def tenant_finance_purchase_detail(empresa_id: int, compra_id: int) -> dict | None:
    c = (
        db.session.query(Compra)
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.compra_id == int(compra_id))
        .first()
    )
    if not c:
        return None

    p = (
        db.session.query(Proveedor)
        .filter(Proveedor.empresa_id == int(empresa_id))
        .filter(Proveedor.proveedor_id == int(c.proveedor_id))
        .first()
    )

    details = (
        db.session.query(CompraDetalle)
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(CompraDetalle.compra_id == int(compra_id))
        .order_by(CompraDetalle.compra_detalle_id.asc())
        .all()
    )

    return {
        "empresa_id": int(empresa_id),
        "compra": {**c.to_dict(), "proveedor_nombre": (p.nombre if p else None)},
        "items": [d.to_dict() for d in details],
    }


def tenant_expenses_series(
    empresa_id: int,
    date_from: str | None,
    date_to: str | None,
    group: str,
) -> dict:
    """
    group: day | month
    """
    g = (group or "day").strip().lower()
    if g not in ("day", "month"):
        g = "day"

    start, end_excl = _dt_range(date_from, date_to)

    if g == "month":
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
        # periodo puede venir date o datetime según expr
        if isinstance(periodo, datetime):
            label = periodo.date().isoformat()
        else:
            label = str(periodo)
        items.append({"periodo": label, "total": float(_dec(total))})

    return {
        "empresa_id": int(empresa_id),
        "from": date_from,
        "to": date_to,
        "group": g,
        "items": items,
    }

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


def tenant_finance_overview(empresa_id: int, date_from: str | None, date_to: str | None) -> dict:
    start, end_excl = _dt_range(date_from, date_to)

    q_exp = (
        db.session.query(
            db.func.coalesce(db.func.sum(Compra.total), 0).label("total"),
            db.func.count(Compra.compra_id).label("n"),
        )
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.estado == "RECIBIDA")
    )

    if start is not None:
        q_exp = q_exp.filter(Compra.fecha_hora >= start)
    if end_excl is not None:
        q_exp = q_exp.filter(Compra.fecha_hora < end_excl)

    exp_total, exp_n = q_exp.first() or (0, 0)
    exp_total = _dec(exp_total)
    exp_n = int(exp_n or 0)

    q_rev = (
        db.session.query(
            db.func.coalesce(db.func.sum(Venta.total), 0).label("total"),
            db.func.count(Venta.venta_id).label("n"),
        )
        .filter(Venta.empresa_id == int(empresa_id))
    )

    if start is not None:
        q_rev = q_rev.filter(Venta.fecha_hora >= start)
    if end_excl is not None:
        q_rev = q_rev.filter(Venta.fecha_hora < end_excl)

    rev_total, rev_n = q_rev.first() or (0, 0)
    rev_total = _dec(rev_total)
    rev_n = int(rev_n or 0)

    profit = rev_total - exp_total
    margin = Decimal("0")
    if rev_total > 0:
        margin = (profit / rev_total) * Decimal("100")

    avg_purchase = Decimal("0")
    if exp_n > 0:
        avg_purchase = exp_total / Decimal(str(exp_n))

    avg_sale = Decimal("0")
    if rev_n > 0:
        avg_sale = rev_total / Decimal(str(rev_n))

    return {
        "empresa_id": int(empresa_id),
        "from": date_from,
        "to": date_to,
        "expenses_total": float(exp_total),
        "revenue_total": float(rev_total),
        "profit_total": float(profit),
        "profit_margin_pct": float(margin),
        "purchases_count": exp_n,
        "sales_count": rev_n,
        "avg_purchase_total": float(avg_purchase),
        "avg_sale_total": float(avg_sale),
    }


def tenant_cashflow_series(empresa_id: int, date_from: str | None, date_to: str | None, group: str) -> dict:
    g = (group or "day").strip().lower()
    if g not in ("day", "month"):
        g = "day"

    start, end_excl = _dt_range(date_from, date_to)

    if g == "month":
        pe = db.func.date_trunc("month", Compra.fecha_hora)
        pr = db.func.date_trunc("month", Venta.fecha_hora)
    else:
        pe = db.func.date(Compra.fecha_hora)
        pr = db.func.date(Venta.fecha_hora)

    q_exp = (
        db.session.query(
            pe.label("p"),
            db.func.coalesce(db.func.sum(Compra.total), 0).label("v"),
        )
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.estado == "RECIBIDA")
    )
    if start is not None:
        q_exp = q_exp.filter(Compra.fecha_hora >= start)
    if end_excl is not None:
        q_exp = q_exp.filter(Compra.fecha_hora < end_excl)
    q_exp = q_exp.group_by("p").order_by("p")

    q_rev = (
        db.session.query(
            pr.label("p"),
            db.func.coalesce(db.func.sum(Venta.total), 0).label("v"),
        )
        .filter(Venta.empresa_id == int(empresa_id))
    )
    if start is not None:
        q_rev = q_rev.filter(Venta.fecha_hora >= start)
    if end_excl is not None:
        q_rev = q_rev.filter(Venta.fecha_hora < end_excl)
    q_rev = q_rev.group_by("p").order_by("p")

    exp_map: dict[str, Decimal] = {}
    for p, v in q_exp.all():
        if isinstance(p, datetime):
            k = p.date().isoformat()
        else:
            k = str(p)
        exp_map[k] = _dec(v)

    rev_map: dict[str, Decimal] = {}
    for p, v in q_rev.all():
        if isinstance(p, datetime):
            k = p.date().isoformat()
        else:
            k = str(p)
        rev_map[k] = _dec(v)

    keys = sorted(set(list(exp_map.keys()) + list(rev_map.keys())))

    items = []
    for k in keys:
        rev = rev_map.get(k, Decimal("0"))
        exp = exp_map.get(k, Decimal("0"))
        prof = rev - exp
        items.append(
            {
                "period": k,
                "revenue": float(rev),
                "expenses": float(exp),
                "profit": float(prof),
            }
        )

    return {
        "empresa_id": int(empresa_id),
        "from": date_from,
        "to": date_to,
        "group": g,
        "items": items,
    }


def tenant_top_products(empresa_id: int, date_from: str | None, date_to: str | None, limit: int, offset: int) -> dict:
    start, end_excl = _dt_range(date_from, date_to)

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
        .offset(int(offset))
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

    return {
        "empresa_id": int(empresa_id),
        "from": date_from,
        "to": date_to,
        "limit": int(limit),
        "offset": int(offset),
        "items": items,
    }


def tenant_top_categories(empresa_id: int, date_from: str | None, date_to: str | None, limit: int, offset: int) -> dict:
    start, end_excl = _dt_range(date_from, date_to)

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
        .offset(int(offset))
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

    return {
        "empresa_id": int(empresa_id),
        "from": date_from,
        "to": date_to,
        "limit": int(limit),
        "offset": int(offset),
        "items": items,
    }


def tenant_inventory_alerts(empresa_id: int, limit: int, offset: int) -> dict:
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
        .offset(int(offset))
    )

    items = []
    for producto_id, codigo, descripcion, stock, stock_min, categoria_nombre in q.all():
        items.append(
            {
                "producto_id": int(producto_id),
                "codigo": str(codigo),
                "descripcion": str(descripcion),
                "stock": float(_dec(stock)),
                "stock_min": int(stock_min or 0),
                "categoria_nombre": categoria_nombre,
            }
        )

    return {
        "empresa_id": int(empresa_id),
        "limit": int(limit),
        "offset": int(offset),
        "items": items,
    }


def tenant_inventory_valuation(empresa_id: int) -> dict:
    price_total = (
            db.session.query(db.func.coalesce(db.func.sum(Producto.stock * Producto.precio), 0))
            .filter(Producto.empresa_id == int(empresa_id))
            .scalar()
            or 0
    )

    sub_cost = (
        db.session.query(
            CompraDetalle.producto_id.label("producto_id"),
            (
                    db.func.sum(CompraDetalle.cantidad * CompraDetalle.costo_unit)
                    / db.func.nullif(db.func.sum(CompraDetalle.cantidad), 0)
            ).label("avg_cost"),
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
        "empresa_id": int(empresa_id),
        "inventory_price_value": float(_dec(price_total)),
        "inventory_avg_cost_value": float(_dec(cost_total)),
    }


def tenant_finance_sales_list(
        empresa_id: int,
        cliente_id: int | None,
        estado: str | None,
        date_from: str | None,
        date_to: str | None,
        limit: int,
        offset: int,
) -> dict:
    start, end_excl = _dt_range(date_from, date_to)
    est = (estado or "").strip().upper() or None

    q = (
        db.session.query(Venta, Cliente.nombre_razon)
        .outerjoin(
            ClienteEmpresa,
            (ClienteEmpresa.empresa_id == Venta.empresa_id) & (ClienteEmpresa.cliente_id == Venta.cliente_id),
            )
        .outerjoin(Cliente, Cliente.cliente_id == ClienteEmpresa.cliente_id)
        .filter(Venta.empresa_id == int(empresa_id))
    )

    if cliente_id:
        q = q.filter(Venta.cliente_id == int(cliente_id))
    if est:
        q = q.filter(Venta.estado == est)
    if start is not None:
        q = q.filter(Venta.fecha_hora >= start)
    if end_excl is not None:
        q = q.filter(Venta.fecha_hora < end_excl)

    q = q.order_by(Venta.fecha_hora.desc(), Venta.venta_id.desc()).limit(int(limit)).offset(int(offset))

    items = []
    for v, cliente_nombre in q.all():
        d = v.to_dict()
        d["cliente_nombre"] = cliente_nombre
        items.append(d)

    return {
        "empresa_id": int(empresa_id),
        "cliente_id": int(cliente_id) if cliente_id else None,
        "estado": est,
        "from": date_from,
        "to": date_to,
        "limit": int(limit),
        "offset": int(offset),
        "items": items,
    }


def tenant_finance_sale_detail(empresa_id: int, venta_id: int) -> dict | None:
    v = (
        db.session.query(Venta)
        .filter(Venta.empresa_id == int(empresa_id))
        .filter(Venta.venta_id == int(venta_id))
        .first()
    )
    if not v:
        return None

    c = (
        db.session.query(Cliente)
        .outerjoin(
            ClienteEmpresa,
            (ClienteEmpresa.empresa_id == int(empresa_id)) & (ClienteEmpresa.cliente_id == Cliente.cliente_id),
            )
        .filter(Cliente.cliente_id == int(v.cliente_id))
        .first()
    )

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

    return {
        "empresa_id": int(empresa_id),
        "venta": {**v.to_dict(), "cliente_nombre": (c.nombre_razon if c else None)},
        "items": items,
    }
