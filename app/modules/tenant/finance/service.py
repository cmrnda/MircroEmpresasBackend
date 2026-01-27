
# app/modules/tenant/finance/service.py
from __future__ import annotations

from datetime import datetime, date, time, timedelta, timezone
from decimal import Decimal

from app.extensions import db
from app.database.models.compra import Compra
from app.database.models.compra_detalle import CompraDetalle
from app.database.models.proveedor import Proveedor


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _parse_ymd(s: str | None) -> date | None:
    s = (s or "").strip()
    if not s:
        return None
    # YYYY-MM-DD
    return datetime.strptime(s, "%Y-%m-%d").date()


def _dt_range(from_ymd: str | None, to_ymd: str | None):
    """
    Convierte YYYY-MM-DD a rango datetime [start, end_exclusive) en UTC.
    Si falta alguno, devuelve None en ese lado.
    """
    d_from = _parse_ymd(from_ymd)
    d_to = _parse_ymd(to_ymd)

    start = None
    end_excl = None

    if d_from:
        start = datetime.combine(d_from, time.min).replace(tzinfo=timezone.utc)

    if d_to:
        # end exclusive = día siguiente 00:00
        end_excl = datetime.combine(d_to + timedelta(days=1), time.min).replace(tzinfo=timezone.utc)

    return start, end_excl


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