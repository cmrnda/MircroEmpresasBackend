from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_platform_admin
from app.modules.platform.users.service import platform_reset_usuario_password

bp = Blueprint("platform_users_api", __name__, url_prefix="/platform/users")

@bp.post("/<int:usuario_id>/reset-password")
@jwt_required()
@require_platform_admin
def reset_password(usuario_id: int):
    data, err = platform_reset_usuario_password(usuario_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify(data), 200
