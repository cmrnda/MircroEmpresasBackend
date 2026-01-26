from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.common.authz import require_platform_admin
from app.common.current import current_usuario_id
from app.extensions import db
from app.modules.notifications.service import NotificationsService
from . import bp


@bp.get("/")
@jwt_required()
@require_platform_admin
def list_notifications():
    usuario_id = current_usuario_id()
    if usuario_id is None:
        return jsonify({"error": "forbidden"}), 403

    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))
    unread_only = request.args.get("unread_only", "0").lower() in ("1", "true", "yes")

    data = NotificationsService.list_notifications_platform_admin(
        int(usuario_id),
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    return jsonify({"data": data}), 200


@bp.get("/unread-count")
@jwt_required()
@require_platform_admin
def unread_count():
    usuario_id = current_usuario_id()
    if usuario_id is None:
        return jsonify({"error": "forbidden"}), 403

    n = NotificationsService.unread_count_platform_admin(int(usuario_id))
    return jsonify({"data": {"unread": n}}), 200


@bp.post("/<int:notificacion_id>/read")
@jwt_required()
@require_platform_admin
def mark_read(notificacion_id: int):
    usuario_id = current_usuario_id()
    if usuario_id is None:
        return jsonify({"error": "forbidden"}), 403

    with db.session.begin():
        data, err = NotificationsService.mark_as_read_platform_admin(int(usuario_id), int(notificacion_id))

    if err == "not_found":
        return jsonify({"error": "not_found"}), 404

    return jsonify({"data": data}), 200
