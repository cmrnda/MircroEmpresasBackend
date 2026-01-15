from datetime import date, timedelta
from app.extensions import db
from app.db.models.suscripcion import Suscripcion
from app.db.models.suscripcion_pago import SuscripcionPago
from app.db.models.plan import Plan

def list_suscripciones():
    return Suscripcion.query.all()

def list_suscripciones_by_empresa(empresa_id):
    return Suscripcion.query.filter_by(empresa_id=empresa_id).all()

def create_suscripcion(empresa_id, plan_id):
    plan = Plan.query.get(plan_id)
    fin = date.today() + timedelta(days=30)

    s = Suscripcion(
        empresa_id=empresa_id,
        plan_id=plan_id,
        estado="PENDIENTE",
        inicio=date.today(),
        fin=fin
    )
    db.session.add(s)
    db.session.commit()
    return s

def create_pago(empresa_id, suscripcion_id, monto, metodo):
    p = SuscripcionPago(
        empresa_id=empresa_id,
        suscripcion_id=suscripcion_id,
        monto=monto,
        metodo=metodo,
        estado="PAGADO"
    )
    db.session.add(p)

    s = Suscripcion.query.get(suscripcion_id)
    s.estado = "ACTIVA"

    db.session.commit()
    return p

def get_suscripcion_activa(empresa_id):
    return Suscripcion.query.filter_by(
        empresa_id=empresa_id,
        estado="ACTIVA"
    ).first()
