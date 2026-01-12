from flask import request

from app.modules.users import users_bp
from app.modules.users.service import UsersService

_service = UsersService()


def _empresa_id_from_request() -> int:
    data = request.get_json(silent=True) or {}
    empresa_id = data.get("empresa_id") or request.headers.get("X-Empresa-Id")
    if not empresa_id:
        raise ValueError("EMPRESA_ID_REQUIRED")
    return int(empresa_id)


@users_bp.post("")
def create_user():
    data = request.get_json() or {}
    empresa_id = _empresa_id_from_request()

    email = data.get("email")
    password = data.get("password")
    roles = data.get("roles") or []

    if not email or not password:
        return {"error": "email and password required"}, 400

    try:
        return {"data": _service.create_user(empresa_id, email, password, roles)}, 201
    except ValueError as e:
        if str(e) == "EMAIL_EXISTS":
            return {"error": "email exists"}, 409
        if str(e) == "EMPRESA_ID_REQUIRED":
            return {"error": "empresa_id required"}, 400
        return {"error": "bad request"}, 400


@users_bp.get("")
def list_users():
    empresa_id = int(request.headers.get("X-Empresa-Id", "0"))
    if empresa_id == 0:
        return {"error": "empresa_id required (X-Empresa-Id)"}, 400
    return {"data": _service.list_users(empresa_id)}, 200


@users_bp.get("/<int:usuario_id>")
def get_user(usuario_id: int):
    empresa_id = int(request.headers.get("X-Empresa-Id", "0"))
    if empresa_id == 0:
        return {"error": "empresa_id required (X-Empresa-Id)"}, 400
    try:
        return {"data": _service.get_user(empresa_id, usuario_id)}, 200
    except ValueError:
        return {"error": "not found"}, 404


@users_bp.put("/<int:usuario_id>")
def update_user(usuario_id: int):
    empresa_id = int(request.headers.get("X-Empresa-Id", "0"))
    if empresa_id == 0:
        return {"error": "empresa_id required (X-Empresa-Id)"}, 400

    data = request.get_json() or {}
    email = data.get("email")
    activo = data.get("activo")

    try:
        return {"data": _service.update_user(empresa_id, usuario_id, email, activo)}, 200
    except ValueError as e:
        if str(e) == "EMAIL_EXISTS":
            return {"error": "email exists"}, 409
        return {"error": "not found"}, 404


@users_bp.patch("/<int:usuario_id>/activar")
def activate_user(usuario_id: int):
    empresa_id = int(request.headers.get("X-Empresa-Id", "0"))
    if empresa_id == 0:
        return {"error": "empresa_id required (X-Empresa-Id)"}, 400

    data = request.get_json() or {}
    activo = data.get("activo")
    if activo is None:
        return {"error": "activo required"}, 400

    try:
        return {"data": _service.update_user(empresa_id, usuario_id, None, bool(activo))}, 200
    except ValueError:
        return {"error": "not found"}, 404


@users_bp.patch("/<int:usuario_id>/roles")
def set_roles(usuario_id: int):
    empresa_id = int(request.headers.get("X-Empresa-Id", "0"))
    if empresa_id == 0:
        return {"error": "empresa_id required (X-Empresa-Id)"}, 400

    data = request.get_json() or {}
    roles = data.get("roles") or []
    if not isinstance(roles, list):
        return {"error": "roles must be list"}, 400

    try:
        return {"data": _service.set_roles(empresa_id, usuario_id, roles)}, 200
    except ValueError:
        return {"error": "not found"}, 404


@users_bp.patch("/<int:usuario_id>/password")
def change_password(usuario_id: int):
    empresa_id = int(request.headers.get("X-Empresa-Id", "0"))
    if empresa_id == 0:
        return {"error": "empresa_id required (X-Empresa-Id)"}, 400

    data = request.get_json() or {}
    new_password = data.get("new_password")
    if not new_password:
        return {"error": "new_password required"}, 400

    try:
        return {"data": _service.change_password(empresa_id, usuario_id, new_password)}, 200
    except ValueError:
        return {"error": "not found"}, 404
