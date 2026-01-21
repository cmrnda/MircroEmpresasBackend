from datetime import datetime, timezone
from app.extensions import db
from app.database.models.producto import Producto
from app.database.models.producto_imagen import ProductoImagen

def get_image(empresa_id: int, producto_id: int):
    return (
        db.session.query(ProductoImagen)
        .filter(ProductoImagen.empresa_id == int(empresa_id))
        .filter(ProductoImagen.producto_id == int(producto_id))
        .first()
    )

def product_exists(empresa_id: int, producto_id: int):
    return (
        db.session.query(Producto)
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.producto_id == int(producto_id))
        .first()
    ) is not None

def upsert_image(empresa_id: int, producto_id: int, payload: dict):
    row = get_image(empresa_id, producto_id)
    if row:
        row.file_path = str(payload.get("file_path")).strip()
        row.url = str(payload.get("url")).strip()
        row.mime_type = str(payload.get("mime_type")).strip()
        row.file_size = int(payload.get("file_size") or 0)
        row.updated_at = datetime.now(timezone.utc)
        db.session.add(row)
        return row
    row = ProductoImagen(
        empresa_id=int(empresa_id),
        producto_id=int(producto_id),
        file_path=str(payload.get("file_path")).strip(),
        url=str(payload.get("url")).strip(),
        mime_type=str(payload.get("mime_type")).strip(),
        file_size=int(payload.get("file_size") or 0),
        updated_at=datetime.now(timezone.utc),
    )
    db.session.add(row)
    return row

def soft_remove_image(empresa_id: int, producto_id: int):
    row = get_image(empresa_id, producto_id)
    if not row:
        return None
    row.file_path = "deleted"
    row.url = "deleted"
    row.mime_type = "application/octet-stream"
    row.file_size = 0
    row.updated_at = datetime.now(timezone.utc)
    db.session.add(row)
    return row
