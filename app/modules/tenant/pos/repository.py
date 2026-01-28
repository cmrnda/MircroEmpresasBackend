from datetime import datetime, timezone
from app.extensions import db
from app.database.models.cliente import Cliente, ClienteEmpresa
from app.database.models.venta import Venta, VentaDetalle
from app.database.models.producto import Producto
from sqlalchemy import text

def get_client_in_tenant_by_id(empresa_id: int, cliente_id: int):
    return (
        db.session.query(Cliente)
        .join(ClienteEmpresa, ClienteEmpresa.cliente_id == Cliente.cliente_id)
        .filter(ClienteEmpresa.empresa_id == int(empresa_id))
        .filter(ClienteEmpresa.cliente_id == int(cliente_id))
        .filter(ClienteEmpresa.activo.is_(True))
        .filter(Cliente.activo.is_(True))
        .first()
    )


def get_client_in_tenant_by_nit(empresa_id: int, nit_ci: str):
    return (
        db.session.query(Cliente)
        .join(ClienteEmpresa, ClienteEmpresa.cliente_id == Cliente.cliente_id)
        .filter(ClienteEmpresa.empresa_id == int(empresa_id))
        .filter(ClienteEmpresa.activo.is_(True))
        .filter(Cliente.activo.is_(True))
        .filter(Cliente.nit_ci == (nit_ci or ""))
        .first()
    )


def ensure_client_link(empresa_id: int, cliente_id: int):
    row = (
        db.session.query(ClienteEmpresa)
        .filter(ClienteEmpresa.empresa_id == int(empresa_id))
        .filter(ClienteEmpresa.cliente_id == int(cliente_id))
        .first()
    )
    if row:
        if not bool(row.activo):
            row.activo = True
            db.session.add(row)
        return row

    row = ClienteEmpresa(
        empresa_id=int(empresa_id),
        cliente_id=int(cliente_id),
        activo=True,
    )
    db.session.add(row)
    return row


def create_client(email: str, password_hash: str, nombre_razon: str, nit_ci=None, telefono=None):
    c = Cliente(
        email=email,
        password_hash=password_hash,
        nombre_razon=nombre_razon,
        nit_ci=nit_ci,
        telefono=telefono,
        activo=True,
    )
    db.session.add(c)
    db.session.flush()
    return c


def lock_products_for_update(empresa_id: int, producto_ids: list[int]):
    if not producto_ids:
        return []
    return (
        db.session.query(Producto)
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.producto_id.in_([int(x) for x in producto_ids]))
        .with_for_update()
        .all()
    )


def create_sale(empresa_id: int, cliente_id: int, payload: dict):
    pago = payload.get("pago") or {}
    v = Venta(
        empresa_id=int(empresa_id),
        cliente_id=int(cliente_id),
        fecha_hora=datetime.now(timezone.utc),
        estado="CONFIRMADA",
        descuento_total=payload.get("descuento_total", 0) or 0,
        envio_costo=0,
        envio_estado=None,
        pago_metodo=(pago.get("metodo") or None),
        pago_monto=(pago.get("monto") if pago.get("monto") is not None else None),
        pago_referencia_qr=(pago.get("referencia_qr") or None),
        pago_estado="PAGADO" if (pago.get("metodo") or None) else None,
        pagado_en=datetime.now(timezone.utc) if (pago.get("metodo") or None) else None,
    )
    db.session.add(v)
    db.session.flush()
    return v


def add_sale_detail(empresa_id: int, venta_id: int, item: dict, precio_unit, subtotal):
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


def set_sale_total(v: Venta, total):
    v.total = total
    db.session.add(v)
    return v


def get_sale_details(empresa_id: int, venta_id: int):
    return (
        db.session.query(VentaDetalle)
        .filter(VentaDetalle.empresa_id == int(empresa_id))
        .filter(VentaDetalle.venta_id == int(venta_id))
        .order_by(VentaDetalle.venta_detalle_id.asc())
        .all()
    )
def get_sale_receipt_data(empresa_id: int, venta_id: int):
    header_sql = text("""
    SELECT
        e.empresa_id,
        e.nombre as empresa_nombre,
        e.nit as empresa_nit,
        NULL as empresa_direccion,
        NULL as empresa_telefono,

        v.venta_id,
        v.fecha_hora,
        v.total,
        v.descuento_total,
        v.estado,
        v.pago_metodo,
        v.pago_monto,
        v.pago_referencia_qr,
        v.pago_estado,
        v.pagado_en,

        c.cliente_id,
        c.nombre_razon as cliente_nombre,
        c.nit_ci as cliente_nit_ci,
        c.telefono as cliente_telefono,
        c.email as cliente_email

    FROM venta v
    JOIN empresa e ON e.empresa_id = v.empresa_id
    LEFT JOIN cliente_empresa ce ON ce.empresa_id = v.empresa_id AND ce.cliente_id = v.cliente_id
    LEFT JOIN cliente c ON c.cliente_id = ce.cliente_id
    WHERE v.empresa_id = :empresa_id AND v.venta_id = :venta_id
    LIMIT 1
""")

    row = db.session.execute(header_sql, {"empresa_id": empresa_id, "venta_id": venta_id}).mappings().first()
    if not row:
        return None

    items_sql = text("""
        SELECT
            vd.producto_id,
            p.codigo as producto_codigo,
            p.descripcion as producto_descripcion,
            vd.cantidad,
            vd.precio_unit,
            vd.descuento,
            vd.subtotal
        FROM venta_detalle vd
        JOIN producto p ON p.empresa_id = vd.empresa_id AND p.producto_id = vd.producto_id
        WHERE vd.empresa_id = :empresa_id AND vd.venta_id = :venta_id
        ORDER BY vd.venta_detalle_id ASC
    """)

    items = db.session.execute(items_sql, {"empresa_id": empresa_id, "venta_id": venta_id}).mappings().all()
    return {"header": dict(row), "items": [dict(x) for x in items]}
