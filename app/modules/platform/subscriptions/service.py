from app.extensions import db
from app.database.models.empresa_settings import EmpresaSettings
from app.database.models.empresa import Empresa

def _get_settings(empresa_id: int):
    return db.session.query(EmpresaSettings).filter(EmpresaSettings.empresa_id == int(empresa_id)).first()

def _ensure_settings(empresa_id: int):
    s = _get_settings(int(empresa_id))
    if s:
        return s
    s = EmpresaSettings(empresa_id=int(empresa_id))
    db.session.add(s)
    db.session.flush()
    return s

def _set_subscription_fields(s: EmpresaSettings, payload: dict):
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

def platform_list_subscriptions(include_inactivos: bool = False):
    q = (
        db.session.query(Empresa, EmpresaSettings)
        .outerjoin(EmpresaSettings, EmpresaSettings.empresa_id == Empresa.empresa_id)
    )

    if not include_inactivos:
        q = q.filter(Empresa.estado == "ACTIVA")

    rows = q.order_by(Empresa.empresa_id.asc()).all()

    items = []
    for e, s in rows:
        items.append({
            "empresa_id": e.empresa_id,
            "empresa_nombre": e.nombre,
            "empresa_estado": e.estado,
            "plan_id": getattr(s, "plan_id", None) if s else None,
            "suscripcion_estado": getattr(s, "suscripcion_estado", None) if s else None,
            "suscripcion_inicio": getattr(s, "suscripcion_inicio", None) if s else None,
            "suscripcion_fin": getattr(s, "suscripcion_fin", None) if s else None,
            "suscripcion_renovacion": getattr(s, "suscripcion_renovacion", None) if s else None,
            "ultimo_pago_monto": getattr(s, "ultimo_pago_monto", None) if s else None,
            "ultimo_pago_moneda": getattr(s, "ultimo_pago_moneda", None) if s else None,
            "ultimo_pago_metodo": getattr(s, "ultimo_pago_metodo", None) if s else None,
            "ultimo_pago_referencia_qr": getattr(s, "ultimo_pago_referencia_qr", None) if s else None,
            "ultimo_pago_estado": getattr(s, "ultimo_pago_estado", None) if s else None,
            "ultimo_pagado_en": getattr(s, "ultimo_pagado_en", None) if s else None,
        })

    return items

def platform_get_subscription(empresa_id: int):
    e = db.session.query(Empresa).filter(Empresa.empresa_id == int(empresa_id)).first()
    if not e:
        return None

    s = _ensure_settings(int(empresa_id))

    return {
        "empresa_id": e.empresa_id,
        "empresa_nombre": e.nombre,
        "empresa_estado": e.estado,
        "plan_id": getattr(s, "plan_id", None),
        "suscripcion_estado": getattr(s, "suscripcion_estado", None),
        "suscripcion_inicio": getattr(s, "suscripcion_inicio", None),
        "suscripcion_fin": getattr(s, "suscripcion_fin", None),
        "suscripcion_renovacion": getattr(s, "suscripcion_renovacion", None),
        "ultimo_pago_monto": getattr(s, "ultimo_pago_monto", None),
        "ultimo_pago_moneda": getattr(s, "ultimo_pago_moneda", None),
        "ultimo_pago_metodo": getattr(s, "ultimo_pago_metodo", None),
        "ultimo_pago_referencia_qr": getattr(s, "ultimo_pago_referencia_qr", None),
        "ultimo_pago_estado": getattr(s, "ultimo_pago_estado", None),
        "ultimo_pagado_en": getattr(s, "ultimo_pagado_en", None),
    }

def platform_update_subscription(empresa_id: int, payload: dict):
    with db.session.begin():
        e = db.session.query(Empresa).filter(Empresa.empresa_id == int(empresa_id)).first()
        if not e:
            return None, "not_found"

        s = _ensure_settings(int(empresa_id))
        _set_subscription_fields(s, payload)

    return platform_get_subscription(int(empresa_id)), None
