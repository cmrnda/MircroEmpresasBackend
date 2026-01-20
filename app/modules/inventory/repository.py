from decimal import Decimal
from app.extensions import db
from app.db.models.producto import Producto
from app.db.models.existencia_producto import ExistenciaProducto
from app.db.models.movimiento_inventario import MovimientoInventario

def list_inventory(empresa_id: int, q: str | None, page: int, page_size: int, include_inactivos: bool):
    page = max(int(page or 1), 1)
    page_size = min(max(int(page_size or 20), 1), 100)

    base = (
        db.session.query(Producto, ExistenciaProducto.cantidad_actual)
        .outerjoin(
            ExistenciaProducto,
            (ExistenciaProducto.empresa_id == Producto.empresa_id)
            & (ExistenciaProducto.producto_id == Producto.producto_id),
            )
        .filter(Producto.empresa_id == empresa_id)
    )

    if not include_inactivos:
        base = base.filter(Producto.activo.is_(True))

    if q:
        like = f"%{q.strip()}%"
        base = base.filter((Producto.codigo.ilike(like)) | (Producto.descripcion.ilike(like)))

    total = base.count()
    rows = (
        base.order_by(Producto.producto_id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return rows, total, page, page_size

def get_existencia_for_update(empresa_id: int, producto_id: int):
    ex = (
        ExistenciaProducto.query
        .filter_by(empresa_id=empresa_id, producto_id=producto_id)
        .with_for_update()
        .first()
    )
    if not ex:
        ex = ExistenciaProducto(empresa_id=empresa_id, producto_id=producto_id, cantidad_actual=Decimal("0"))
        db.session.add(ex)
        db.session.flush()
    return ex

def create_movimiento(empresa_id: int, producto_id: int, tipo: str, cantidad: Decimal, ref_tabla: str | None, ref_id: int | None, usuario_id: int):
    m = MovimientoInventario(
        empresa_id=empresa_id,
        producto_id=producto_id,
        tipo=tipo,
        cantidad=cantidad,
        ref_tabla=ref_tabla,
        ref_id=ref_id,
        realizado_por_usuario_id=usuario_id,
    )
    db.session.add(m)
    return m
