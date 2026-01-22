from app.extensions import db
from app.database.models.compra import Compra

def tenant_get_expenses_summary(empresa_id: int, date_from=None, date_to=None):
    q = db.session.query(db.func.coalesce(db.func.sum(Compra.total), 0)).filter(Compra.empresa_id == int(empresa_id)).filter(Compra.estado == "RECIBIDA")
    if date_from:
        q = q.filter(Compra.fecha_hora >= date_from)
    if date_to:
        q = q.filter(Compra.fecha_hora <= date_to)
    total = q.scalar()
    return {"empresa_id": int(empresa_id), "compras_total": float(total) if total is not None else 0}
