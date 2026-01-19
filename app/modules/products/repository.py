from app.extensions import db
from app.db.models.producto import Producto
from app.db.models.categoria import Categoria

def list_products(
    empresa_id: int,
    include_inactivos: bool = False,
    categoria_id: int | None = None,
    q: str | None = None,
):
    query = Producto.query.filter(Producto.empresa_id == empresa_id)

    if not include_inactivos:
        query = query.filter(Producto.activo.is_(True))

    if categoria_id is not None:
        query = query.filter(Producto.categoria_id == int(categoria_id))

    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (Producto.codigo.ilike(like)) | (Producto.descripcion.ilike(like))
        )

    return query.order_by(Producto.producto_id.desc()).all()

def get_product(empresa_id: int, producto_id: int, include_inactivos: bool = False):
    q = Producto.query.filter_by(empresa_id=empresa_id, producto_id=producto_id)
    if not include_inactivos:
        q = q.filter(Producto.activo.is_(True))
    return q.first()

def get_product_any(empresa_id: int, producto_id: int):
    return Producto.query.filter_by(empresa_id=empresa_id, producto_id=producto_id).first()

def get_active_category(empresa_id: int, categoria_id: int):
    return Categoria.query.filter_by(
        empresa_id=empresa_id, categoria_id=categoria_id, activo=True
    ).first()

def create_product(empresa_id: int, payload: dict):
    p = Producto(
        empresa_id=empresa_id,
        categoria_id=int(payload.get("categoria_id")),
        codigo=(payload.get("codigo") or "").strip(),
        descripcion=(payload.get("descripcion") or "").strip(),
        precio=payload.get("precio"),
        stock_min=payload.get("stock_min") if payload.get("stock_min") is not None else 0,
        activo=True,
    )
    db.session.add(p)
    db.session.commit()
    return p

def update_product(p: Producto, payload: dict):
    if payload.get("categoria_id") is not None:
        p.categoria_id = int(payload.get("categoria_id"))

    if payload.get("codigo") is not None:
        p.codigo = (payload.get("codigo") or "").strip()

    if payload.get("descripcion") is not None:
        p.descripcion = (payload.get("descripcion") or "").strip()

    if payload.get("precio") is not None:
        p.precio = payload.get("precio")

    if payload.get("stock_min") is not None:
        p.stock_min = int(payload.get("stock_min"))

    if payload.get("activo") is not None:
        p.activo = bool(payload.get("activo"))

    db.session.commit()
    return p

def soft_delete_product(p: Producto):
    p.activo = False
    db.session.commit()
    return p

def restore_product(p: Producto):
    p.activo = True
    db.session.commit()
    return p
