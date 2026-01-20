import os

from flask import send_from_directory, current_app, abort

from app.modules.media import bp


@bp.get("/<path:filepath>")
def get_media(filepath):
    root = current_app.config.get("UPLOAD_ROOT", "uploads")
    safe_root = os.path.abspath(root)
    abs_path = os.path.abspath(os.path.join(safe_root, filepath))

    if not abs_path.startswith(safe_root + os.sep) and abs_path != safe_root:
        abort(404)

    if not os.path.exists(abs_path):
        abort(404)

    dir_name = os.path.dirname(abs_path)
    base_name = os.path.basename(abs_path)
    return send_from_directory(dir_name, base_name)
