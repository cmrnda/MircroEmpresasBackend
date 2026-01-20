from app.extensions import db
from app.db.models.producto import Producto
from app.db.models.producto_imagen import ProductoImagen

def get_producto(empresa_id: int, producto_id: int):
    return Producto.query.filter_by(empresa_id=empresa_id, producto_id=producto_id).first()

def list_images(empresa_id: int, producto_id: int):
    return (
        ProductoImagen.query
        .filter_by(empresa_id=empresa_id, producto_id=producto_id)
        .order_by(ProductoImagen.is_primary.desc(), ProductoImagen.image_id.desc())
        .all()
    )

def create_image(empresa_id: int, producto_id: int, file_path: str, url: str, mime_type: str, file_size: int, is_primary: bool):
    img = ProductoImagen(
        empresa_id=empresa_id,
        producto_id=producto_id,
        file_path=file_path,
        url=url,
        mime_type=mime_type,
        file_size=int(file_size or 0),
        is_primary=bool(is_primary),
    )
    db.session.add(img)
    db.session.flush()
    return img

def get_image(empresa_id: int, producto_id: int, image_id: int):
    return ProductoImagen.query.filter_by(empresa_id=empresa_id, producto_id=producto_id, image_id=image_id).first()

def unset_primary(empresa_id: int, producto_id: int):
    (
        ProductoImagen.query
        .filter_by(empresa_id=empresa_id, producto_id=producto_id, is_primary=True)
        .update({"is_primary": False})
    )

def set_primary(img: ProductoImagen):
    img.is_primary = True

def delete_image(img: ProductoImagen):
    db.session.delete(img)
