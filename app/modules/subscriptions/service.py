from datetime import date, datetime, timedelta

from app.extensions import db
from app.modules.subscriptions.repository import (
    get_empresa,
    set_empresa_estado,
    list_plans,
    get_plan,
    list_suscripciones,
    list_suscripciones_by_empresa,
    get_latest_suscripcion,
    get_suscripcion,
    get_last_pago,
    create_suscripcion,
    create_pago,
)


def tenant_list_plans():
    return tenant_plans()


def _is_active(s, today: date) -> bool:
    return bool(s and s.estado == "ACTIVA" and s.fin and s.fin >= today)


def _activate_extend(s, today: date, days: int = 30):
    base = s.fin if (s.fin and s.fin > today) else today
    new_fin = base + timedelta(days=days)
    s.estado = "ACTIVA"
    s.fin = new_fin
    s.renovacion = new_fin
    return new_fin


def tenant_plans():
    items = list_plans()
    return [p.to_dict() for p in items]


def tenant_status(empresa_id: int):
    today = date.today()
    e = get_empresa(empresa_id)
    s = get_latest_suscripcion(empresa_id)

    plan = get_plan(s.plan_id) if s else None
    last_pago = get_last_pago(empresa_id, s.suscripcion_id) if s else None

    is_active = _is_active(s, today)
    remaining_days = (s.fin - today).days if (s and s.fin) else None

    return {
        "empresa_id": int(empresa_id),
        "empresa_estado": e.estado if e else None,
        "suscripcion": s.to_dict() if s else None,
        "plan": plan.to_dict() if plan else None,
        "is_active": bool(is_active),
        "remaining_days": remaining_days,
        "last_pago": last_pago.to_dict() if last_pago else None,
    }


def tenant_select_plan(empresa_id: int, payload: dict):
    plan_id = payload.get("plan_id")
    if not plan_id:
        return None, "invalid_payload"

    plan = get_plan(int(plan_id))
    if not plan:
        return None, "invalid_plan"

    s = create_suscripcion(empresa_id, plan.plan_id)
    db.session.commit()

    return {"suscripcion": s.to_dict(), "plan": plan.to_dict()}, None


def tenant_pay(empresa_id: int, payload: dict):
    suscripcion_id = payload.get("suscripcion_id")
    monto = payload.get("monto")
    metodo = payload.get("metodo")
    moneda = payload.get("moneda") or "BOB"
    referencia_qr = payload.get("referencia_qr")

    if not suscripcion_id or monto is None or not metodo:
        return None, "invalid_payload"

    s = get_suscripcion(empresa_id, int(suscripcion_id))
    if not s:
        return None, "not_found"

    plan = get_plan(int(s.plan_id))
    if not plan:
        return None, "invalid_plan"

    if float(monto) != float(plan.precio):
        return None, "invalid_amount"

    now = datetime.utcnow()
    today = date.today()

    p = create_pago(
        empresa_id=empresa_id,
        suscripcion_id=s.suscripcion_id,
        monto=monto,
        moneda=moneda,
        metodo=metodo,
        referencia_qr=referencia_qr,
        estado="PAGADO",
        pagado_en=now,
    )

    _activate_extend(s, today, days=30)
    set_empresa_estado(empresa_id, "ACTIVA")

    db.session.commit()

    return {
        "pago": p.to_dict(),
        "suscripcion": s.to_dict(),
        "plan": plan.to_dict(),
    }, None


def platform_list(empresa_id: int | None):
    subs = list_suscripciones_by_empresa(empresa_id) if empresa_id else list_suscripciones()
    return [s.to_dict() for s in subs]


def platform_create(payload: dict):
    empresa_id = payload.get("empresa_id")
    plan_id = payload.get("plan_id")
    if not empresa_id or not plan_id:
        return None, "invalid_payload"

    plan = get_plan(int(plan_id))
    if not plan:
        return None, "invalid_plan"

    s = create_suscripcion(int(empresa_id), int(plan_id))
    db.session.commit()
    return s.to_dict(), None


def platform_pay(payload: dict):
    empresa_id = payload.get("empresa_id")
    suscripcion_id = payload.get("suscripcion_id")
    monto = payload.get("monto")
    metodo = payload.get("metodo")
    moneda = payload.get("moneda") or "BOB"
    referencia_qr = payload.get("referencia_qr")

    if not empresa_id or not suscripcion_id or monto is None or not metodo:
        return None, "invalid_payload"

    s = get_suscripcion(int(empresa_id), int(suscripcion_id))
    if not s:
        return None, "not_found"

    plan = get_plan(int(s.plan_id))
    if not plan:
        return None, "invalid_plan"

    now = datetime.utcnow()
    today = date.today()

    p = create_pago(
        empresa_id=int(empresa_id),
        suscripcion_id=s.suscripcion_id,
        monto=monto,
        moneda=moneda,
        metodo=metodo,
        referencia_qr=referencia_qr,
        estado="PAGADO",
        pagado_en=now,
    )

    _activate_extend(s, today, days=30)
    set_empresa_estado(int(empresa_id), "ACTIVA")

    db.session.commit()
    return {"pago": p.to_dict(), "suscripcion": s.to_dict()}, None
