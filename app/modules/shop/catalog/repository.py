from app.extensions import db
from app.database.models.catalogo import Categoria, Producto, ProductoImagen
from app.common.paging import page_args

def list_categories(empresa_id: int):
    return (
        db.session.query(Categoria)
        .filter(Categoria.empresa_id == int(empresa_id))
        .filter(Categoria.activo.is_(True))
        .order_by(Categoria.categoria_id.asc())
        .all()
    )

def get_primary_image_url(empresa_id: int, producto_id: int):
    row = (
        db.session.query(ProductoImagen)
        .filter(ProductoImagen.empresa_id == int(empresa_id))
        .filter(ProductoImagen.producto_id == int(producto_id))
        .first()
    )
    return row.url if row else None

def list_products(empresa_id: int, q=None, categoria_id=None, page=1, page_size=20):
    query = (
        db.session.query(Producto)
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.activo.is_(True))
    )
    if categoria_id is not None:
        query = query.filter(Producto.categoria_id == int(categoria_id))
    if q:
        qq = f"%{q}%"
        query = query.filter(Producto.codigo.ilike(qq) | Producto.descripcion.ilike(qq))
    total = query.count()
    items = (
        query.order_by(Producto.producto_id.asc())
        .offset((int(page) - 1) * int(page_size))
        .limit(int(page_size))
        .all()
    )
    return items, total

def get_product(empresa_id: int, producto_id: int):
    return (
        db.session.query(Producto)
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.producto_id == int(producto_id))
        .filter(Producto.activo.is_(True))
        .first()
    )
