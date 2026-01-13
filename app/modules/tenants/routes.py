from flask import Blueprint, request
from app.common.authz import require_scope, require_role
from app.modules.tenants.service import TenantsService

tenants_bp = Blueprint("tenants", __name__)
_service = TenantsService()

@tenants_bp.post("/platform/tenants")
@require_scope("PLATFORM")
@require_role("ADMIN_PLATAFORMA")
def create_tenant():
    data = request.get_json() or {}
    return _service.create_tenant_with_admin(data)

@tenants_bp.get("/platform/tenants")
@require_scope("PLATFORM")
@require_role("ADMIN_PLATAFORMA")
def list_tenants():
    return _service.list_tenants()

@tenants_bp.get("/platform/tenants/<int:empresa_id>")
@require_scope("PLATFORM")
@require_role("ADMIN_PLATAFORMA")
def get_tenant(empresa_id: int):
    return _service.get_tenant(empresa_id)

@tenants_bp.patch("/platform/tenants/<int:empresa_id>/status")
@require_scope("PLATFORM")
@require_role("ADMIN_PLATAFORMA")
def set_tenant_status(empresa_id: int):
    data = request.get_json() or {}
    return _service.set_tenant_status(empresa_id, data)

@tenants_bp.get("/platform/plans")
@require_scope("PLATFORM")
@require_role("ADMIN_PLATAFORMA")
def list_plans():
    return _service.list_plans()

@tenants_bp.post("/platform/plans")
@require_scope("PLATFORM")
@require_role("ADMIN_PLATAFORMA")
def create_plan():
    data = request.get_json() or {}
    return _service.create_plan(data)

@tenants_bp.post("/platform/tenants/<int:empresa_id>/subscriptions")
@require_scope("PLATFORM")
@require_role("ADMIN_PLATAFORMA")
def create_subscription(empresa_id: int):
    data = request.get_json() or {}
    return _service.create_subscription(empresa_id, data)

@tenants_bp.post("/platform/tenants/<int:empresa_id>/subscription-payments")
@require_scope("PLATFORM")
@require_role("ADMIN_PLATAFORMA")
def create_subscription_payment(empresa_id: int):
    data = request.get_json() or {}
    return _service.create_subscription_payment(empresa_id, data)
