from app.extensions import db
from app.modules.tenant.product_image.repository import (
    product_exists,
    upsert_image,
    get_image,
    soft_remove_image,
)

def tenant_get_image(empresa_id: int, producto_id: int):
    row = get_image(empresa_id, producto_id)
    return row.to_dict() if row else None

def tenant_set_image(empresa_id: int, producto_id: int, payload: dict):
    required = ["file_path", "url", "mime_type"]
    for k in required:
        if payload.get(k) is None or str(payload.get(k)).strip() == "":
            return None, "invalid_payload"

    if not product_exists(empresa_id, producto_id):
        return None, "not_found"

    row = upsert_image(empresa_id, producto_id, payload)
    db.session.commit()
    return row.to_dict(), None

def tenant_remove_image(empresa_id: int, producto_id: int):
    row = soft_remove_image(empresa_id, producto_id)
    if not row:
        db.session.rollback()
        return None
    db.session.commit()
    return row.to_dict()
