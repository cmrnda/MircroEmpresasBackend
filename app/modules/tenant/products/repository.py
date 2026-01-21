from app.extensions import db
from app.database.models.catalogo import Producto, Categoria, ProductoImagen

def list_products(empresa_id: int, q=None, categoria_id=None, include_inactivos=False):
    query = db.session.query(Producto).filter(Producto.empresa_id == int(empresa_id))
    if not include_inactivos:
        query = query.filter(Producto.activo.is_(True))
    if categoria_id is not None:
        query = query.filter(Producto.categoria_id == int(categoria_id))
    if q:
        qq = f"%{q}%"
        query = query.filter(
            Producto.codigo.ilike(qq) | Producto.descripcion.ilike(qq)
        )
    return query.order_by(Producto.producto_id.asc()).all()

def get_product_any(empresa_id: int, producto_id: int):
    return (
        db.session.query(Producto)
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.producto_id == int(producto_id))
        .first()
    )

def get_product(empresa_id: int, producto_id: int, include_inactivos=False):
    q = (
        db.session.query(Producto)
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.producto_id == int(producto_id))
    )
    if not include_inactivos:
        q = q.filter(Producto.activo.is_(True))
    return q.first()

def create_product(empresa_id: int, payload: dict):
    p = Producto(
        empresa_id=int(empresa_id),
        categoria_id=int(payload.get("categoria_id")),
        codigo=str(payload.get("codigo")).strip(),
        descripcion=str(payload.get("descripcion")).strip(),
        precio=payload.get("precio", 0),
        stock=payload.get("stock", 0),
        stock_min=payload.get("stock_min", 0),
        activo=True,
    )
    db.session.add(p)
    db.session.flush()
    return p

def update_product(p: Producto, payload: dict):
    if "categoria_id" in payload and payload.get("categoria_id") is not None:
        p.categoria_id = int(payload.get("categoria_id"))
    if "codigo" in payload and payload.get("codigo") is not None:
        p.codigo = str(payload.get("codigo")).strip()
    if "descripcion" in payload and payload.get("descripcion") is not None:
        p.descripcion = str(payload.get("descripcion")).strip()
    if "precio" in payload and payload.get("precio") is not None:
        p.precio = payload.get("precio")
    if "stock" in payload and payload.get("stock") is not None:
        p.stock = payload.get("stock")
    if "stock_min" in payload and payload.get("stock_min") is not None:
        p.stock_min = payload.get("stock_min")
    db.session.add(p)
    return p

def soft_delete_product(p: Producto):
    p.activo = False
    db.session.add(p)
    return p

def restore_product(p: Producto):
    p.activo = True
    db.session.add(p)
    return p

def category_exists(empresa_id: int, categoria_id: int):
    return (
        db.session.query(Categoria)
        .filter(Categoria.empresa_id == int(empresa_id))
        .filter(Categoria.categoria_id == int(categoria_id))
        .filter(Categoria.activo.is_(True))
        .first()
    ) is not None

def get_primary_image_url(empresa_id: int, producto_id: int):
    row = (
        db.session.query(ProductoImagen)
        .filter(ProductoImagen.empresa_id == int(empresa_id))
        .filter(ProductoImagen.producto_id == int(producto_id))
        .first()
    )
    return row.url if row else None
