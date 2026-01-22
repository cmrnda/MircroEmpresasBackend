# app/modules/tenant/purchases/repository.py

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from app.extensions import db
from app.database.models.compra import Compra
from app.database.models.compra_detalle import CompraDetalle
from app.database.models.producto import Producto
from app.database.models.proveedor import Proveedor


def supplier_exists(empresa_id: int, proveedor_id: int) -> bool:
    row = (
        db.session.query(Proveedor.proveedor_id)
        .filter(Proveedor.empresa_id == int(empresa_id))
        .filter(Proveedor.proveedor_id == int(proveedor_id))
        .filter(Proveedor.activo.is_(True))
        .first()
    )
    return bool(row)


def product_exists(empresa_id: int, producto_id: int) -> bool:
    row = (
        db.session.query(Producto.producto_id)
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.producto_id == int(producto_id))
        .first()
    )
    return bool(row)


def list_purchases(empresa_id: int, proveedor_id=None, estado=None):
    q = db.session.query(Compra).filter(Compra.empresa_id == int(empresa_id))
    if proveedor_id is not None:
        q = q.filter(Compra.proveedor_id == int(proveedor_id))
    if estado:
        q = q.filter(Compra.estado == str(estado).strip())
    return q.order_by(Compra.compra_id.desc()).all()


def get_purchase(empresa_id: int, compra_id: int):
    return (
        db.session.query(Compra)
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.compra_id == int(compra_id))
        .first()
    )


def get_purchase_for_update(empresa_id: int, compra_id: int):
    return (
        db.session.query(Compra)
        .filter(Compra.empresa_id == int(empresa_id))
        .filter(Compra.compra_id == int(compra_id))
        .with_for_update()
        .first()
    )


def list_purchase_details(empresa_id: int, compra_id: int):
    return (
        db.session.query(CompraDetalle)
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(CompraDetalle.compra_id == int(compra_id))
        .order_by(CompraDetalle.compra_detalle_id.asc())
        .all()
    )


def create_purchase(empresa_id: int, proveedor_id: int, observacion: str | None):
    c = Compra(
        empresa_id=int(empresa_id),
        proveedor_id=int(proveedor_id),
        observacion=observacion or None,
        estado="CREADA",
        total=0,
    )
    db.session.add(c)
    db.session.flush()
    return c


def add_purchase_detail(empresa_id: int, compra_id: int, producto_id: int, cantidad, costo_unit):
    try:
        cantidad_d = Decimal(str(cantidad))
        costo_d = Decimal(str(costo_unit))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("invalid_item")

    if cantidad_d <= 0:
        raise ValueError("invalid_item")
    if costo_d < 0:
        raise ValueError("invalid_item")

    subtotal = (cantidad_d * costo_d).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    d = CompraDetalle(
        empresa_id=int(empresa_id),
        compra_id=int(compra_id),
        producto_id=int(producto_id),
        cantidad=cantidad_d,
        costo_unit=costo_d,
        subtotal=subtotal,
    )
    db.session.add(d)
    db.session.flush()
    return d


def recompute_total(empresa_id: int, compra_id: int):
    total = (
        db.session.query(db.func.coalesce(db.func.sum(CompraDetalle.subtotal), 0))
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(CompraDetalle.compra_id == int(compra_id))
        .scalar()
    )
    row = get_purchase(empresa_id, compra_id)
    row.total = total
    db.session.add(row)
    return row


def mark_received(c: Compra, usuario_id: int):
    c.estado = "RECIBIDA"
    c.recibido_por_usuario_id = int(usuario_id)
    c.recibido_en = db.func.now()
    db.session.add(c)
    return c


def mark_canceled(c: Compra):
    c.estado = "ANULADA"
    db.session.add(c)
    return c


def apply_stock_increase(empresa_id: int, compra_id: int):
    det = (
        db.session.query(CompraDetalle)
        .filter(CompraDetalle.empresa_id == int(empresa_id))
        .filter(CompraDetalle.compra_id == int(compra_id))
        .order_by(CompraDetalle.compra_detalle_id.asc())
        .all()
    )

    for d in det:
        p = (
            db.session.query(Producto)
            .filter(Producto.empresa_id == int(empresa_id))
            .filter(Producto.producto_id == int(d.producto_id))
            .with_for_update()
            .first()
        )
        if not p:
            continue

        stock_actual = p.stock if p.stock is not None else Decimal("0")
        inc = d.cantidad if d.cantidad is not None else Decimal("0")

        p.stock = stock_actual + inc
        db.session.add(p)

    return True
