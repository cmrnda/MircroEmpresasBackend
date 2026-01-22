from datetime import datetime, timezone
from decimal import Decimal
from app.extensions import db
from app.database.models.venta import Venta, VentaDetalle
from app.database.models.producto import Producto
from app.database.models.cliente import ClienteEmpresa
from app.database.models.usuario import UsuarioAdminEmpresa, UsuarioVendedor
from app.modules.notifications.repository import create_for_user

def cliente_in_tenant(empresa_id: int, cliente_id: int):
    return (
        db.session.query(ClienteEmpresa)
        .filter(ClienteEmpresa.empresa_id == int(empresa_id))
        .filter(ClienteEmpresa.cliente_id == int(cliente_id))
        .filter(ClienteEmpresa.activo.is_(True))
        .first()
    ) is not None

def lock_products_for_update(empresa_id: int, producto_ids: list[int]):
    if not producto_ids:
        return []
    rows = (
        db.session.query(Producto)
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.producto_id.in_([int(x) for x in producto_ids]))
        .with_for_update()
        .all()
    )
    return rows

def create_order(empresa_id: int, cliente_id: int, payload: dict):
    v = Venta(
        empresa_id=int(empresa_id),
        cliente_id=int(cliente_id),
        fecha_hora=datetime.now(timezone.utc),
        estado="CREADA",
        descuento_total=payload.get("descuento_total", 0) or 0,
        envio_departamento=(payload.get("envio_departamento") or None),
        envio_ciudad=(payload.get("envio_ciudad") or None),
        envio_zona_barrio=(payload.get("envio_zona_barrio") or None),
        envio_direccion_linea=(payload.get("envio_direccion_linea") or None),
        envio_referencia=(payload.get("envio_referencia") or None),
        envio_telefono_receptor=(payload.get("envio_telefono_receptor") or None),
        envio_costo=payload.get("envio_costo", 0) or 0,
        envio_estado="PENDIENTE",
    )
    db.session.add(v)
    db.session.flush()
    return v

def add_detail(empresa_id: int, venta_id: int, item: dict, precio_unit, subtotal):
    d = VentaDetalle(
        empresa_id=int(empresa_id),
        venta_id=int(venta_id),
        producto_id=int(item.get("producto_id")),
        cantidad=item.get("cantidad"),
        precio_unit=precio_unit,
        descuento=item.get("descuento", 0) or 0,
        subtotal=subtotal,
    )
    db.session.add(d)
    return d

def set_order_total(v: Venta, total):
    v.total = total
    db.session.add(v)
    return v

def notify_tenant_new_order(empresa_id: int, venta_id: int):
    ids = set()
    rows_a = db.session.query(UsuarioAdminEmpresa.usuario_id).filter(UsuarioAdminEmpresa.empresa_id == int(empresa_id)).all()
    rows_v = db.session.query(UsuarioVendedor.usuario_id).filter(UsuarioVendedor.empresa_id == int(empresa_id)).all()
    for r in rows_a:
        ids.add(int(r[0]))
    for r in rows_v:
        ids.add(int(r[0]))
    titulo = "Nuevo pedido"
    cuerpo = f"Pedido {int(venta_id)} creado"
    for uid in ids:
        create_for_user(empresa_id, uid, "IN_APP", titulo, cuerpo)

# def notify_client_created(empresa_id: int, cliente_id: int, venta_id: int):
#    create_for_client(empresa_id, cliente_id, "IN_APP", "Pedido creado", f"Pedido {int(venta_id)} creado")

def list_client_orders(empresa_id: int, cliente_id: int):
    rows = (
        db.session.query(Venta)
        .filter(Venta.empresa_id == int(empresa_id))
        .filter(Venta.cliente_id == int(cliente_id))
        .order_by(Venta.venta_id.desc())
        .all()
    )
    return rows

def get_client_order(empresa_id: int, cliente_id: int, venta_id: int):
    return (
        db.session.query(Venta)
        .filter(Venta.empresa_id == int(empresa_id))
        .filter(Venta.cliente_id == int(cliente_id))
        .filter(Venta.venta_id == int(venta_id))
        .first()
    )

def get_details(empresa_id: int, venta_id: int):
    return (
        db.session.query(VentaDetalle)
        .filter(VentaDetalle.empresa_id == int(empresa_id))
        .filter(VentaDetalle.venta_id == int(venta_id))
        .order_by(VentaDetalle.venta_detalle_id.asc())
        .all()
    )
