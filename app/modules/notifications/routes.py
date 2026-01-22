from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.modules.notifications import bp
from app.modules.notifications.service import NotificationsService
from app.common.current import current_empresa_id, current_usuario_id
from app.common.authz import require_tenant_user
from app.extensions import db


def _is_tenant_admin() -> bool:
    roles = (get_jwt() or {}).get("roles") or []
    return "TENANT_ADMIN" in roles


@bp.get("/")
@jwt_required()
@require_tenant_user
def list_notifications():
    empresa_id = current_empresa_id()
    usuario_id = current_usuario_id()
    if empresa_id is None or usuario_id is None:
        return jsonify({"error": "forbidden"}), 403

    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))
    unread_only = request.args.get("unread_only", "0").lower() in ("1", "true", "yes")

    include_all = _is_tenant_admin()

    data = NotificationsService.list_notifications(
        int(empresa_id),
        int(usuario_id),
        include_all=include_all,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    return jsonify({"data": data}), 200


@bp.get("/unread-count")
@jwt_required()
@require_tenant_user
def unread_count():
    empresa_id = current_empresa_id()
    usuario_id = current_usuario_id()
    if empresa_id is None or usuario_id is None:
        return jsonify({"error": "forbidden"}), 403

    include_all = _is_tenant_admin()
    n = NotificationsService.unread_count(int(empresa_id), int(usuario_id), include_all=include_all)
    return jsonify({"data": {"unread": n}}), 200


@bp.post("/<int:notificacion_id>/read")
@jwt_required()
@require_tenant_user
def mark_read(notificacion_id: int):
    empresa_id = current_empresa_id()
    usuario_id = current_usuario_id()
    if empresa_id is None or usuario_id is None:
        return jsonify({"error": "forbidden"}), 403

    include_all = _is_tenant_admin()

    with db.session.begin():
        data, err = NotificationsService.mark_as_read(
            int(empresa_id),
            int(usuario_id),
            include_all=include_all,
            notificacion_id=int(notificacion_id),
        )

    if err == "not_found":
        return jsonify({"error": "not_found"}), 404
    if err == "forbidden":
        return jsonify({"error": "forbidden"}), 403

    return jsonify({"data": data}), 200
