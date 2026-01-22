from datetime import datetime, timezone
from app.extensions import db
from app.database.models.venta import Venta, VentaDetalle

def list_orders(empresa_id: int, estado=None, cliente_id=None):
    q = db.session.query(Venta).filter(Venta.empresa_id == int(empresa_id))
    if estado:
        q = q.filter(Venta.estado == str(estado).strip())
    if cliente_id is not None:
        q = q.filter(Venta.cliente_id == int(cliente_id))
    return q.order_by(Venta.venta_id.desc()).all()

def get_order(empresa_id: int, venta_id: int):
    return (
        db.session.query(Venta)
        .filter(Venta.empresa_id == int(empresa_id))
        .filter(Venta.venta_id == int(venta_id))
        .first()
    )

def get_order_details(empresa_id: int, venta_id: int):
    return (
        db.session.query(VentaDetalle)
        .filter(VentaDetalle.empresa_id == int(empresa_id))
        .filter(VentaDetalle.venta_id == int(venta_id))
        .order_by(VentaDetalle.venta_detalle_id.asc())
        .all()
    )

def set_order_status(v: Venta, estado: str, usuario_id: int | None):
    v.estado = str(estado).strip()
    if usuario_id is not None:
        v.confirmado_por_usuario_id = int(usuario_id)
        v.confirmado_en = datetime.now(timezone.utc)
    db.session.add(v)
    return v

def set_shipping(v: Venta, payload: dict, usuario_id: int):
    v.envio_estado = (payload.get("envio_estado") or "DESPACHADO")
    v.envio_tracking = (payload.get("envio_tracking") or v.envio_tracking)
    v.envio_fecha_despacho = datetime.now(timezone.utc)
    v.estado = "DESPACHADA"
    v.confirmado_por_usuario_id = int(usuario_id)
    v.confirmado_en = datetime.now(timezone.utc)
    db.session.add(v)
    return v

def set_delivered(v: Venta, usuario_id: int):
    v.envio_estado = "ENTREGADO"
    v.envio_fecha_entrega = datetime.now(timezone.utc)
    v.estado = "ENTREGADA"
    v.confirmado_por_usuario_id = int(usuario_id)
    v.confirmado_en = datetime.now(timezone.utc)
    db.session.add(v)
    return v
