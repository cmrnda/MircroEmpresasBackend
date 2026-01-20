from app.extensions import db
from app.db.models.venta import Venta
from app.db.models.venta_envio import VentaEnvio
from app.db.models.venta_detalle import VentaDetalle

def list_ventas(empresa_id: int, estado: str | None, page: int, page_size: int):
    page = max(int(page or 1), 1)
    page_size = min(max(int(page_size or 20), 1), 100)

    q = Venta.query.filter(Venta.empresa_id == empresa_id)

    if estado:
        q = q.filter(Venta.estado == estado)

    total = q.count()
    items = (
        q.order_by(Venta.venta_id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total, page, page_size

def get_venta(empresa_id: int, venta_id: int):
    return Venta.query.filter_by(empresa_id=empresa_id, venta_id=venta_id).first()

def get_envio(empresa_id: int, venta_id: int):
    return VentaEnvio.query.filter_by(empresa_id=empresa_id, venta_id=venta_id).first()

def list_detalles(empresa_id: int, venta_id: int):
    return (
        VentaDetalle.query
        .filter_by(empresa_id=empresa_id, venta_id=venta_id)
        .order_by(VentaDetalle.venta_detalle_id.asc())
        .all()
    )

def set_envio_despachado(envio: VentaEnvio, tracking: str | None):
    envio.estado_envio = "DESPACHADO"
    envio.tracking = tracking or envio.tracking
    envio.fecha_despacho = db.func.now()

def set_envio_entregado(envio: VentaEnvio):
    envio.estado_envio = "ENTREGADO"
    envio.fecha_entrega = db.func.now()

def set_venta_estado(venta: Venta, estado: str, confirmado_por_usuario_id: int | None = None):
    venta.estado = estado
    if confirmado_por_usuario_id is not None:
        venta.confirmado_por_usuario_id = confirmado_por_usuario_id
        venta.confirmado_en = db.func.now()
