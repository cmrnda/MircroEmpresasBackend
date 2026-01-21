from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.platform.plans.repository import list_plans, get_plan, create_plan, update_plan

def platform_list_plans():
    return [p.to_dict() for p in list_plans()]

def platform_get_plan(plan_id: int):
    p = get_plan(int(plan_id))
    return p.to_dict() if p else None

def platform_create_plan(payload: dict):
    nombre = (payload.get("nombre") or "").strip()
    periodo_cobro = (payload.get("periodo_cobro") or "").strip()
    precio = payload.get("precio")

    if not nombre or not periodo_cobro or precio is None:
        return None, "invalid_payload"

    try:
        with db.session.begin():
            p = create_plan(nombre, precio, periodo_cobro)
        return p.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"

def platform_update_plan(plan_id: int, payload: dict):
    try:
        with db.session.begin():
            p = get_plan(int(plan_id))
            if not p:
                return None, "not_found"
            update_plan(p, payload)
        return p.to_dict(), None
    except IntegrityError:
        db.session.rollback()
        return None, "conflict"
