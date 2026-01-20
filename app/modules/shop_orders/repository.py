from decimal import Decimal
from app.extensions import db
from app.db.models.cliente import Cliente
from app.db.models.producto import Producto
from app.db.models.existencia_producto import ExistenciaProducto
from app.db.models.movimiento_inventario import MovimientoInventario
from app.db.models.venta import Venta
from app.db.models.venta_detalle import VentaDetalle
from app.db.models.venta_envio import VentaEnvio

def get_cliente(empresa_id: int, cliente_id: int):
    return Cliente.query.filter_by(empresa_id=empresa_id, cliente_id=cliente_id, activo=True).first()

def get_productos_for_update(empresa_id: int, producto_ids: list[int]):
    rows = (
        db.session.query(Producto, ExistenciaProducto)
        .outerjoin(
            ExistenciaProducto,
            (ExistenciaProducto.empresa_id == Producto.empresa_id)
            & (ExistenciaProducto.producto_id == Producto.producto_id),
            )
        .filter(
            Producto.empresa_id == empresa_id,
            Producto.producto_id.in_(producto_ids),
            Producto.activo.is_(True),
            )
        .with_for_update()
        .all()
    )
    return rows

def ensure_existencia_row(empresa_id: int, producto_id: int):
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

def create_venta(empresa_id: int, cliente_id: int, total: Decimal):
    v = Venta(
        empresa_id=empresa_id,
        cliente_id=cliente_id,
        total=total,
        descuento_total=Decimal("0"),
        estado="CREADA",
    )
    db.session.add(v)
    db.session.flush()
    return v

def add_venta_detalle(empresa_id: int, venta_id: int, producto_id: int, cantidad: Decimal, precio_unit: Decimal):
    subtotal = (cantidad * precio_unit)
    d = VentaDetalle(
        empresa_id=empresa_id,
        venta_id=venta_id,
        producto_id=producto_id,
        cantidad=cantidad,
        precio_unit=precio_unit,
        descuento=Decimal("0"),
        subtotal=subtotal,
    )
    db.session.add(d)
    return d

def create_envio(empresa_id: int, venta_id: int, envio: dict):
    e = VentaEnvio(
        empresa_id=empresa_id,
        venta_id=venta_id,
        departamento=(envio.get("departamento") or "").strip(),
        ciudad=(envio.get("ciudad") or "").strip(),
        zona_barrio=(envio.get("zona_barrio") or "").strip() or None,
        direccion_linea=(envio.get("direccion_linea") or "").strip(),
        referencia=(envio.get("referencia") or "").strip() or None,
        telefono_receptor=(envio.get("telefono_receptor") or "").strip() or None,
        costo_envio=Decimal(str(envio.get("costo_envio") or "0")),
        estado_envio="PENDIENTE",
        tracking=None,
    )
    db.session.add(e)
    return e

def add_movimiento(empresa_id: int, producto_id: int, tipo: str, cantidad: Decimal, ref_tabla: str, ref_id: int, usuario_id: int):
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

def list_my_ventas(empresa_id: int, cliente_id: int, page: int, page_size: int):
    page = max(int(page or 1), 1)
    page_size = min(max(int(page_size or 20), 1), 100)

    base = (
        Venta.query
        .filter_by(empresa_id=empresa_id, cliente_id=cliente_id)
        .order_by(Venta.venta_id.desc())
    )
    total = base.count()
    items = base.offset((page - 1) * page_size).limit(page_size).all()
    return items, total, page, page_size

def get_my_venta(empresa_id: int, cliente_id: int, venta_id: int):
    return Venta.query.filter_by(empresa_id=empresa_id, cliente_id=cliente_id, venta_id=venta_id).first()

def list_venta_detalles(empresa_id: int, venta_id: int):
    return (
        VentaDetalle.query
        .filter_by(empresa_id=empresa_id, venta_id=venta_id)
        .order_by(VentaDetalle.venta_detalle_id.asc())
        .all()
    )

def get_envio(empresa_id: int, venta_id: int):
    return VentaEnvio.query.filter_by(empresa_id=empresa_id, venta_id=venta_id).first()
