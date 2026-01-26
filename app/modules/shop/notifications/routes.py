from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.common.authz import require_client
from app.common.current import current_empresa_id, current_cliente_id
from app.modules.notifications.service import NotificationsService
from app.extensions import db


bp = Blueprint("shop_notifications_api", __name__, url_prefix="/shop")


@bp.get("/<int:empresa_id>/notifications")
@jwt_required()
@require_client
def list_notifications(empresa_id: int):
    token_empresa_id = int(current_empresa_id())
    if int(empresa_id) != int(token_empresa_id):
        return jsonify({"error": "forbidden_empresa"}), 403

    cliente_id = int(current_cliente_id())
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))
    unread_only = request.args.get("unread_only", "0").lower() in ("1", "true", "yes")

    data = NotificationsService.list_notifications_client(
        int(empresa_id),
        int(cliente_id),
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    return jsonify({"data": data}), 200


@bp.get("/<int:empresa_id>/notifications/unread-count")
@jwt_required()
@require_client
def unread_count(empresa_id: int):
    token_empresa_id = int(current_empresa_id())
    if int(empresa_id) != int(token_empresa_id):
        return jsonify({"error": "forbidden_empresa"}), 403

    cliente_id = int(current_cliente_id())
    n = NotificationsService.unread_count_client(int(empresa_id), int(cliente_id))
    return jsonify({"data": {"unread": n}}), 200


@bp.post("/<int:empresa_id>/notifications/<int:notificacion_id>/read")
@jwt_required()
@require_client
def mark_read(empresa_id: int, notificacion_id: int):
    token_empresa_id = int(current_empresa_id())
    if int(empresa_id) != int(token_empresa_id):
        return jsonify({"error": "forbidden_empresa"}), 403

    cliente_id = int(current_cliente_id())

    with db.session.begin():
        data, err = NotificationsService.mark_as_read_client(int(empresa_id), int(cliente_id), int(notificacion_id))

    if err == "not_found":
        return jsonify({"error": "not_found"}), 404

    return jsonify({"data": data}), 200
