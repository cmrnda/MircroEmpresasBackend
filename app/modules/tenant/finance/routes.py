from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id
from app.modules.tenant.finance.service import tenant_get_expenses_summary

bp = Blueprint("tenant_finance_api", __name__, url_prefix="/tenant/finance")

@bp.get("/expenses")
@jwt_required()
@require_tenant_admin
def expenses():
    empresa_id = int(current_empresa_id())
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    return jsonify(tenant_get_expenses_summary(empresa_id, date_from=date_from, date_to=date_to)), 200
