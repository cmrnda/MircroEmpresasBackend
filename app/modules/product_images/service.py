import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db
from app.modules.product_images.repository import (
    get_producto,
    list_images,
    create_image,
    get_image,
    unset_primary,
    set_primary,
    delete_image,
)

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}


def _img_dict(i):
    return {
        "image_id": int(i.image_id),
        "url": i.url,
        "mime_type": i.mime_type,
        "file_size": int(i.file_size or 0),
        "is_primary": bool(i.is_primary),
        "created_at": i.created_at.isoformat() if i.created_at else None,
    }


def tenant_list_product_images(empresa_id: int, producto_id: int):
    p = get_producto(empresa_id, producto_id)
    if not p:
        return None, "not_found"
    return [_img_dict(i) for i in list_images(empresa_id, producto_id)], None


def tenant_upload_product_image(empresa_id: int, producto_id: int, file_storage, set_as_primary: bool):
    p = get_producto(empresa_id, producto_id)
    if not p:
        return None, "not_found"

    if not file_storage:
        return None, "invalid_payload"

    mime = (file_storage.mimetype or "").lower()
    if mime not in ALLOWED_MIME:
        return None, "invalid_file_type"

    upload_root = current_app.config.get("UPLOAD_ROOT", "uploads")
    ext = os.path.splitext(secure_filename(file_storage.filename or ""))[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        if mime == "image/jpeg":
            ext = ".jpg"
        elif mime == "image/png":
            ext = ".png"
        else:
            ext = ".webp"

    name = f"{uuid.uuid4().hex}{ext}"
    rel_dir = os.path.join(str(empresa_id), "products", str(producto_id))
    abs_dir = os.path.join(upload_root, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)

    abs_path = os.path.join(abs_dir, name)
    file_storage.save(abs_path)

    rel_path = os.path.join(rel_dir, name).replace("\\", "/")
    url = f"/media/{rel_path}"
    size = os.path.getsize(abs_path) if os.path.exists(abs_path) else 0

    with db.session.begin_nested():
        if set_as_primary:
            unset_primary(empresa_id, producto_id)
        img = create_image(empresa_id, producto_id, rel_path, url, mime, size, set_as_primary)

    db.session.commit()
    return _img_dict(img), None


def tenant_set_primary_image(empresa_id: int, producto_id: int, image_id: int):
    img = get_image(empresa_id, producto_id, image_id)
    if not img:
        return None, "not_found"

    with db.session.begin_nested():
        unset_primary(empresa_id, producto_id)
        set_primary(img)

    db.session.commit()
    return _img_dict(img), None


def tenant_delete_product_image(empresa_id: int, producto_id: int, image_id: int):
    img = get_image(empresa_id, producto_id, image_id)
    if not img:
        return None, "not_found"

    upload_root = current_app.config.get("UPLOAD_ROOT", "uploads")
    abs_path = os.path.join(upload_root, img.file_path)

    with db.session.begin_nested():
        delete_image(img)

    db.session.commit()

    try:
        if abs_path and os.path.exists(abs_path):
            os.remove(abs_path)
    except Exception:
        pass

    return {"ok": True}, None
