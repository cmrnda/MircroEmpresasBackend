from __future__ import annotations

from decimal import Decimal
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert

from app.extensions import db
from app.database.models.proveedor import Proveedor
from app.database.models.producto import Producto
from app.database.models.proveedor_producto import ProveedorProducto
from app.database.models.compra import Compra, CompraDetalle


def _dt_iso(v):
    return v.isoformat() if v else None


def _num(v):
    if v is None:
        return 0.0
    try:
        return float(v)
    except Exception:
        return float(Decimal(str(v)))


def _purchase_to_dict(c: Compra, p: Proveedor | None):
    return {
        "compra_id": int(getattr(c, "compra_id")),
        "empresa_id": int(getattr(c, "empresa_id")),
        "proveedor_id": int(getattr(c, "proveedor_id")),
        "fecha_hora": _dt_iso(getattr(c, "fecha_hora", None)),
        "total": _num(getattr(c, "total", 0)),
        "estado": str(getattr(c, "estado", "")),
        "observacion": getattr(c, "observacion", None),
        "recibido_por_usuario_id": int(getattr(c, "recibido_por_usuario_id")) if getattr(c, "recibido_por_usuario_id", None) is not None else None,
        "recibido_en": _dt_iso(getattr(c, "recibido_en", None)),
        "proveedor": p.to_dict() if p else None,
    }


def _detail_to_dict(d: CompraDetalle, pr: Producto | None):
    prod = None
    if pr:
        prod = {
            "producto_id": int(pr.producto_id),
            "empresa_id": int(pr.empresa_id),
            "categoria_id": int(pr.categoria_id),
            "codigo": pr.codigo,
            "descripcion": pr.descripcion,
            "image_url": pr.image_url,
        }

    return {
        "compra_detalle_id": int(getattr(d, "compra_detalle_id")),
        "empresa_id": int(getattr(d, "empresa_id")),
        "compra_id": int(getattr(d, "compra_id")),
        "producto_id": int(getattr(d, "producto_id")),
        "cantidad": _num(getattr(d, "cantidad", 0)),
        "costo_unit": _num(getattr(d, "costo_unit", 0)),
        "subtotal": _num(getattr(d, "subtotal", 0)),
        "lote": getattr(d, "lote", None),
        "fecha_vencimiento": getattr(d, "fecha_vencimiento", None).isoformat() if getattr(d, "fecha_vencimiento", None) else None,
        "producto": prod,
    }


def supplier_exists(empresa_id: int, proveedor_id: int) -> bool:
    x = (
        db.session.query(Proveedor.proveedor_id)
        .filter(Proveedor.empresa_id == int(empresa_id))
        .filter(Proveedor.proveedor_id == int(proveedor_id))
        .first()
    )
    return bool(x)


def product_exists(empresa_id: int, producto_id: int) -> bool:
    x = (
        db.session.query(Producto.producto_id)
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.producto_id == int(producto_id))
        .first()
    )
    return bool(x)


def upsert_proveedor_producto(empresa_id: int, proveedor_id: int, producto_id: int) -> None:
    stmt = (
        insert(ProveedorProducto)
        .values(
            empresa_id=int(empresa_id),
            proveedor_id=int(proveedor_id),
            producto_id=int(producto_id),
        )
        .on_conflict_do_nothing(index_elements=["empresa_id", "proveedor_id", "producto_id"])
    )
    db.session.execute(stmt)


def list_purchases(empresa_id: int, proveedor_id: int | None = None, estado: str | None = None):
    q = (
        db.session.query(Compra, Proveedor)
        .outerjoin(
            Proveedor,
            and_(Proveedor.empresa_id == Compra.empresa_id, Proveedor.proveedor_id == Compra.proveedor_id),
        )
        .filter(Compra.empresa_id == int(empresa_id))
        .order_by(Compra.compra_id.desc())
    )
    if proveedor_id is not None:
        q = q.filter(Compra.proveedor_id == int(proveedor_id))
    if estado is not None:
        q = q.filter(Compra.estado == str(estado))

    rows = q.all()
    return [_purchase_to_dict(c, p) for (c, p) in rows]


def get_purchase(empresa_id: int, compra_id: int):
    row = (
        db.session.query(Compra, Proveedor)
        .outerjoin(
            Proveedor,
            and_(Proveedor.empresa_id == Compra.empresa_id, Proveedor.proveedor_id == Compra.proveedor_id),
        )
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.compra_id == int(compra_id))
        .first()
    )
    if not row:
        return None
    c, p = row
    return _purchase_to_dict(c, p)


def get_purchase_for_update(empresa_id: int, compra_id: int):
    return (
        db.session.query(Compra)
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.compra_id == int(compra_id))
        .with_for_update()
        .first()
    )


def list_purchase_details(empresa_id: int, compra_id: int):
    rows = (
        db.session.query(CompraDetalle, Producto)
        .outerjoin(
            Producto,
            and_(Producto.empresa_id == CompraDetalle.empresa_id, Producto.producto_id == CompraDetalle.producto_id),
        )
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(CompraDetalle.compra_id == int(compra_id))
        .order_by(CompraDetalle.compra_detalle_id.asc())
        .all()
    )
    return [_detail_to_dict(d, p) for (d, p) in rows]


def get_purchase_detail_for_update(empresa_id: int, compra_id: int, compra_detalle_id: int):
    return (
        db.session.query(CompraDetalle)
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(CompraDetalle.compra_id == int(compra_id))
        .filter(CompraDetalle.compra_detalle_id == int(compra_detalle_id))
        .with_for_update()
        .first()
    )


def create_purchase(empresa_id: int, proveedor_id: int, observacion: str | None):
    c = Compra(
        empresa_id=int(empresa_id),
        proveedor_id=int(proveedor_id),
        observacion=observacion,
        estado="CREADA",
        total=0,
    )
    db.session.add(c)
    db.session.flush()
    return c


def add_purchase_detail(
        empresa_id: int,
        compra_id: int,
        producto_id: int,
        cantidad,
        costo_unit,
        lote=None,
        fecha_vencimiento=None,
):
    qty = Decimal(str(cantidad))
    cost = Decimal(str(costo_unit))
    sub = qty * cost

    d = CompraDetalle(
        empresa_id=int(empresa_id),
        compra_id=int(compra_id),
        producto_id=int(producto_id),
        cantidad=qty,
        costo_unit=cost,
        subtotal=sub,
        lote=(str(lote).strip() if lote is not None and str(lote).strip() else None),
        fecha_vencimiento=fecha_vencimiento,
    )
    db.session.add(d)
    db.session.flush()
    return d


def update_purchase_detail(d: CompraDetalle, cantidad=None, costo_unit=None, lote=None, fecha_vencimiento=None):
    if cantidad is not None:
        d.cantidad = Decimal(str(cantidad))
    if costo_unit is not None:
        d.costo_unit = Decimal(str(costo_unit))
    if lote is not None:
        d.lote = (str(lote).strip() if str(lote).strip() else None)
    if fecha_vencimiento is not None:
        d.fecha_vencimiento = fecha_vencimiento

    d.subtotal = Decimal(str(d.cantidad)) * Decimal(str(d.costo_unit))
    db.session.flush()
    return d


def delete_purchase_detail(d: CompraDetalle):
    db.session.delete(d)
    db.session.flush()


def recompute_total(empresa_id: int, compra_id: int):
    total = (
        db.session.query(func.coalesce(func.sum(CompraDetalle.subtotal), 0))
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(CompraDetalle.compra_id == int(compra_id))
        .scalar()
    )

    db.session.query(Compra).filter(Compra.empresa_id == int(empresa_id)).filter(Compra.compra_id == int(compra_id)).update(
        {"total": total}
    )
    db.session.flush()
    return total


def apply_stock_increase(empresa_id: int, compra_id: int):
    dets = (
        db.session.query(CompraDetalle)
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(CompraDetalle.compra_id == int(compra_id))
        .all()
    )

    for d in dets:
        db.session.query(Producto).filter(Producto.empresa_id == int(empresa_id)).filter(Producto.producto_id == int(d.producto_id)).update(
            {Producto.stock: Producto.stock + d.cantidad}
        )
    db.session.flush()


def mark_received(c: Compra, usuario_id: int):
    c.estado = "RECIBIDA"
    c.recibido_por_usuario_id = int(usuario_id)
    c.recibido_en = db.func.now()
    db.session.flush()
    return c


def mark_canceled(c: Compra):
    c.estado = "ANULADA"
    db.session.flush()
    return c
