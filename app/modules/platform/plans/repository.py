from app.extensions import db
from app.database.models.plan import Plan

def list_plans():
    return db.session.query(Plan).order_by(Plan.plan_id.asc()).all()

def get_plan(plan_id: int):
    return db.session.query(Plan).filter(Plan.plan_id == int(plan_id)).first()

def create_plan(nombre: str, precio, periodo_cobro: str):
    p = Plan(nombre=nombre, precio=precio, periodo_cobro=periodo_cobro)
    db.session.add(p)
    db.session.flush()
    return p

def update_plan(p: Plan, payload: dict):
    if "nombre" in payload and payload.get("nombre") is not None:
        p.nombre = str(payload.get("nombre")).strip()
    if "precio" in payload and payload.get("precio") is not None:
        p.precio = payload.get("precio")
    if "periodo_cobro" in payload and payload.get("periodo_cobro") is not None:
        p.periodo_cobro = str(payload.get("periodo_cobro")).strip()
    db.session.add(p)
    return p
