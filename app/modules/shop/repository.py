from app.extensions import db
from app.db.models.categoria import Categoria
from app.db.models.producto import Producto
from app.db.models.existencia_producto import ExistenciaProducto
from app.db.models.producto_imagen import ProductoImagen

def list_public_categories(empresa_id: int):
    return (
        Categoria.query
        .filter(Categoria.empresa_id == empresa_id, Categoria.activo.is_(True))
        .order_by(Categoria.categoria_id.desc())
        .all()
    )

def list_public_products(
        empresa_id: int,
        categoria_id: int | None,
        q: str | None,
        page: int,
        page_size: int,
):
    page = max(int(page or 1), 1)
    page_size = min(max(int(page_size or 20), 1), 100)

    primary_url = (
        db.session.query(ProductoImagen.url)
        .filter(
            ProductoImagen.empresa_id == empresa_id,
            ProductoImagen.producto_id == Producto.producto_id,
            ProductoImagen.is_primary.is_(True),
            )
        .order_by(ProductoImagen.image_id.desc())
        .limit(1)
        .correlate(Producto)
        .scalar_subquery()
    )

    base = (
        db.session.query(
            Producto,
            ExistenciaProducto.cantidad_actual,
            primary_url.label("primary_image_url"),
        )
        .outerjoin(
            ExistenciaProducto,
            (ExistenciaProducto.empresa_id == Producto.empresa_id)
            & (ExistenciaProducto.producto_id == Producto.producto_id),
            )
        .filter(
            Producto.empresa_id == empresa_id,
            Producto.activo.is_(True),
            )
    )

    if categoria_id is not None:
        base = base.filter(Producto.categoria_id == int(categoria_id))

    if q:
        like = f"%{q.strip()}%"
        base = base.filter((Producto.codigo.ilike(like)) | (Producto.descripcion.ilike(like)))

    total = base.count()

    rows = (
        base.order_by(Producto.producto_id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return rows, total, page, page_size

def get_public_product(empresa_id: int, producto_id: int):
    primary = (
        ProductoImagen.query
        .filter_by(empresa_id=empresa_id, producto_id=producto_id, is_primary=True)
        .order_by(ProductoImagen.image_id.desc())
        .first()
    )

    row = (
        db.session.query(Producto, ExistenciaProducto.cantidad_actual)
        .outerjoin(
            ExistenciaProducto,
            (ExistenciaProducto.empresa_id == Producto.empresa_id)
            & (ExistenciaProducto.producto_id == Producto.producto_id),
            )
        .filter(
            Producto.empresa_id == empresa_id,
            Producto.producto_id == producto_id,
            Producto.activo.is_(True),
            )
        .first()
    )

    return row, (primary.url if primary else None)
