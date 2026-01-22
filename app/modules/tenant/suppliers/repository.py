from app.extensions import db
from app.database.models.proveedor import Proveedor

def list_suppliers(empresa_id: int, q=None, include_inactivos=False):
    query = db.session.query(Proveedor).filter(Proveedor.empresa_id == int(empresa_id))
    if not include_inactivos:
        query = query.filter(Proveedor.activo.is_(True))
    if q:
        qq = f"%{q}%"
        query = query.filter(Proveedor.nombre.ilike(qq) | Proveedor.nit.ilike(qq))
    return query.order_by(Proveedor.proveedor_id.asc()).all()

def get_supplier(empresa_id: int, proveedor_id: int, include_inactivos=False):
    q = db.session.query(Proveedor).filter(Proveedor.empresa_id == int(empresa_id)).filter(Proveedor.proveedor_id == int(proveedor_id))
    if not include_inactivos:
        q = q.filter(Proveedor.activo.is_(True))
    return q.first()

def get_supplier_any(empresa_id: int, proveedor_id: int):
    return db.session.query(Proveedor).filter(Proveedor.empresa_id == int(empresa_id)).filter(Proveedor.proveedor_id == int(proveedor_id)).first()

def create_supplier(empresa_id: int, payload: dict):
    s = Proveedor(
        empresa_id=int(empresa_id),
        nombre=str(payload.get("nombre")).strip(),
        nit=(payload.get("nit") or "").strip() or None,
        telefono=(payload.get("telefono") or "").strip() or None,
        direccion=(payload.get("direccion") or "").strip() or None,
        email=(payload.get("email") or "").strip() or None,
        activo=True,
    )
    db.session.add(s)
    db.session.flush()
    return s

def update_supplier(s: Proveedor, payload: dict):
    if "nombre" in payload and payload.get("nombre") is not None:
        s.nombre = str(payload.get("nombre")).strip()
    if "nit" in payload:
        s.nit = (payload.get("nit") or "").strip() or None
    if "telefono" in payload:
        s.telefono = (payload.get("telefono") or "").strip() or None
    if "direccion" in payload:
        s.direccion = (payload.get("direccion") or "").strip() or None
    if "email" in payload:
        s.email = (payload.get("email") or "").strip() or None
    if "activo" in payload and payload.get("activo") is not None:
        s.activo = bool(payload.get("activo"))
    db.session.add(s)
    return s

def soft_delete_supplier(s: Proveedor):
    s.activo = False
    db.session.add(s)
    return s

def restore_supplier(s: Proveedor):
    s.activo = True
    db.session.add(s)
    return s
