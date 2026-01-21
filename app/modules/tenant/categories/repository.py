from app.extensions import db
from app.database.models.catalogo import Categoria

def list_categories(empresa_id: int, q=None, include_inactivos=False):
    query = db.session.query(Categoria).filter(Categoria.empresa_id == int(empresa_id))
    if not include_inactivos:
        query = query.filter(Categoria.activo.is_(True))
    if q:
        qq = f"%{q}%"
        query = query.filter(Categoria.nombre.ilike(qq))
    return query.order_by(Categoria.categoria_id.asc()).all()

def get_category_any(empresa_id: int, categoria_id: int):
    return (
        db.session.query(Categoria)
        .filter(Categoria.empresa_id == int(empresa_id))
        .filter(Categoria.categoria_id == int(categoria_id))
        .first()
    )

def get_category(empresa_id: int, categoria_id: int, include_inactivos=False):
    q = (
        db.session.query(Categoria)
        .filter(Categoria.empresa_id == int(empresa_id))
        .filter(Categoria.categoria_id == int(categoria_id))
    )
    if not include_inactivos:
        q = q.filter(Categoria.activo.is_(True))
    return q.first()

def create_category(empresa_id: int, nombre: str):
    c = Categoria(empresa_id=int(empresa_id), nombre=str(nombre).strip(), activo=True)
    db.session.add(c)
    db.session.flush()
    return c

def update_category(c: Categoria, payload: dict):
    if "nombre" in payload and payload.get("nombre") is not None:
        c.nombre = str(payload.get("nombre")).strip()
    db.session.add(c)
    return c

def soft_delete_category(c: Categoria):
    c.activo = False
    db.session.add(c)
    return c

def restore_category(c: Categoria):
    c.activo = True
    db.session.add(c)
    return c
