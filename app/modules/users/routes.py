from flask import Blueprint, request, g
from app.common.authz import require_scope, require_empresa_id, require_role
from app.modules.users.service import UsersService

users_bp = Blueprint("users", __name__)
_service = UsersService()

@users_bp.get("/tenant/users")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def list_users():
    return _service.list_users(int(g.empresa_id))

@users_bp.post("/tenant/users")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def create_user():
    data = request.get_json() or {}
    return _service.create_user(int(g.empresa_id), data)

@users_bp.get("/tenant/users/<int:usuario_id>")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def get_user(usuario_id: int):
    return _service.get_user(int(g.empresa_id), usuario_id)

@users_bp.put("/tenant/users/<int:usuario_id>/roles")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def set_roles(usuario_id: int):
    data = request.get_json() or {}
    return _service.set_roles(int(g.empresa_id), usuario_id, data)

@users_bp.patch("/tenant/users/<int:usuario_id>/status")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def set_status(usuario_id: int):
    data = request.get_json() or {}
    return _service.set_status(int(g.empresa_id), usuario_id, data)

@users_bp.put("/tenant/users/<int:usuario_id>/password")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def set_password(usuario_id: int):
    data = request.get_json() or {}
    return _service.set_password(usuario_id, data)
