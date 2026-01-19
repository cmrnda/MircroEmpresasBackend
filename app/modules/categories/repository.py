from app.extensions import db
from app.db.models.categoria import Categoria

def list_categories(empresa_id: int, include_inactivos: bool = False):
    q = Categoria.query.filter_by(empresa_id=empresa_id)
    if not include_inactivos:
        q = q.filter(Categoria.activo.is_(True))
    return q.order_by(Categoria.categoria_id.desc()).all()

def get_category(empresa_id: int, categoria_id: int, include_inactivos: bool = False):
    q = Categoria.query.filter_by(empresa_id=empresa_id, categoria_id=categoria_id)
    if not include_inactivos:
        q = q.filter(Categoria.activo.is_(True))
    return q.first()

def get_category_any(empresa_id: int, categoria_id: int):
    # trae aunque esté inactiva
    return Categoria.query.filter_by(empresa_id=empresa_id, categoria_id=categoria_id).first()

def create_category(empresa_id: int, nombre: str):
    c = Categoria(empresa_id=empresa_id, nombre=nombre.strip(), activo=True)
    db.session.add(c)
    db.session.commit()
    return c

def update_category(c: Categoria, payload: dict):
    if payload.get("nombre") is not None:
        c.nombre = (payload.get("nombre") or "").strip()
    if payload.get("activo") is not None:
        c.activo = bool(payload.get("activo"))
    db.session.commit()
    return c

def soft_delete_category(c: Categoria):
    c.activo = False
    db.session.commit()
    return c

def restore_category(c: Categoria):
    c.activo = True
    db.session.commit()
    return c