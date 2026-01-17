from datetime import date
from app.extensions import db
from app.db.models.empresa import Empresa
from app.db.models.plan import Plan
from app.db.models.suscripcion import Suscripcion
from app.db.models.suscripcion_pago import SuscripcionPago


def get_empresa(empresa_id: int):
    return Empresa.query.filter_by(empresa_id=empresa_id).first()


def set_empresa_estado(empresa_id: int, estado: str):
    e = Empresa.query.filter_by(empresa_id=empresa_id).first()
    if not e:
        return None
    e.estado = estado
    return e


def list_plans():
    return Plan.query.order_by(Plan.plan_id.asc()).all()


def get_plan(plan_id: int):
    return Plan.query.filter_by(plan_id=plan_id).first()


def list_suscripciones():
    return Suscripcion.query.order_by(Suscripcion.suscripcion_id.desc()).all()


def list_suscripciones_by_empresa(empresa_id: int):
    return (
        Suscripcion.query
        .filter_by(empresa_id=empresa_id)
        .order_by(Suscripcion.suscripcion_id.desc())
        .all()
    )


def get_latest_suscripcion(empresa_id: int):
    return (
        Suscripcion.query
        .filter_by(empresa_id=empresa_id)
        .order_by(Suscripcion.suscripcion_id.desc())
        .first()
    )


def get_suscripcion(empresa_id: int, suscripcion_id: int):
    return Suscripcion.query.filter_by(empresa_id=empresa_id, suscripcion_id=suscripcion_id).first()


def get_last_pago(empresa_id: int, suscripcion_id: int):
    return (
        SuscripcionPago.query
        .filter_by(empresa_id=empresa_id, suscripcion_id=suscripcion_id)
        .order_by(SuscripcionPago.pago_suscripcion_id.desc())
        .first()
    )


def create_suscripcion(empresa_id: int, plan_id: int):
    s = Suscripcion(
        empresa_id=empresa_id,
        plan_id=plan_id,
        estado="PENDIENTE",
        inicio=date.today(),
        fin=date.today(),
        renovacion=date.today(),
    )
    db.session.add(s)
    db.session.flush()
    return s


def create_pago(
        empresa_id: int,
        suscripcion_id: int,
        monto,
        moneda: str,
        metodo: str,
        referencia_qr: str | None,
        estado: str,
        pagado_en,
):
    p = SuscripcionPago(
        empresa_id=empresa_id,
        suscripcion_id=suscripcion_id,
        monto=monto,
        moneda=moneda or "BOB",
        metodo=metodo,
        referencia_qr=referencia_qr,
        estado=estado,
        pagado_en=pagado_en,
    )
    db.session.add(p)
    db.session.flush()
    return p
