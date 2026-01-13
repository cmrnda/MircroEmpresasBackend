from flask import Blueprint, request, g
from app.common.authz import require_scope, require_empresa_id, require_role
from app.modules.clients.service import ClientsService

clients_bp = Blueprint("clients", __name__)
_service = ClientsService()

@clients_bp.get("/tenant/clients")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def list_clients():
    return _service.list_clients(int(g.empresa_id))

@clients_bp.post("/tenant/clients")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def create_client():
    data = request.get_json() or {}
    return _service.create_client(int(g.empresa_id), data)

@clients_bp.put("/tenant/clients/<int:cliente_id>")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def update_client(cliente_id: int):
    data = request.get_json() or {}
    return _service.update_client(int(g.empresa_id), cliente_id, data)

@clients_bp.patch("/tenant/clients/<int:cliente_id>/status")
@require_scope("TENANT")
@require_empresa_id
@require_role("ADMIN_EMPRESA")
def set_client_status(cliente_id: int):
    data = request.get_json() or {}
    return _service.set_client_status(int(g.empresa_id), cliente_id, data)

@clients_bp.get("/client/me")
@require_scope("CLIENT")
@require_empresa_id
def client_me():
    return _service.client_me(int(g.empresa_id), int(g.usuario_id))

@clients_bp.put("/client/me")
@require_scope("CLIENT")
@require_empresa_id
def client_me_update():
    data = request.get_json() or {}
    return _service.client_me_update(int(g.empresa_id), int(g.usuario_id), data)
