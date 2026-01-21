from app.extensions import db
from app.database.models.empresa_settings import EmpresaSettings
from app.database.models.empresa import Empresa

def get_settings(empresa_id: int):
    return db.session.query(EmpresaSettings).filter(EmpresaSettings.empresa_id == int(empresa_id)).first()

def ensure_settings(empresa_id: int):
    s = get_settings(int(empresa_id))
    if s:
        return s
    s = EmpresaSettings(empresa_id=int(empresa_id))
    db.session.add(s)
    db.session.flush()
    return s

def set_subscription_fields(s: EmpresaSettings, payload: dict):
    allowed = {
        "plan_id",
        "suscripcion_estado",
        "suscripcion_inicio",
        "suscripcion_fin",
        "suscripcion_renovacion",
        "ultimo_pago_monto",
        "ultimo_pago_moneda",
        "ultimo_pago_metodo",
        "ultimo_pago_referencia_qr",
        "ultimo_pago_estado",
        "ultimo_pagado_en",
    }
    for k in allowed:
        if k in payload:
            setattr(s, k, payload.get(k))
    db.session.add(s)
    return s

def list_tenants_with_settings(include_inactivos=False):
    q = db.session.query(Empresa, EmpresaSettings).outerjoin(EmpresaSettings, EmpresaSettings.empresa_id == Empresa.empresa_id)
    if not include_inactivos:
        q = q.filter(Empresa.estado == "ACTIVA")
    return q.order_by(Empresa.empresa_id.asc()).all()
