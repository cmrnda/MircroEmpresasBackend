from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id

from app.modules.tenant.finance.service import (
    tenant_expenses_total,
    tenant_expenses_by_supplier,
    tenant_suppliers_summary,
    tenant_finance_purchases_list,
    tenant_finance_purchase_detail,
    tenant_expenses_series,
)

bp = Blueprint("tenant_finance_api", __name__, url_prefix="/tenant/finance")


def _int_arg(name: str, default: int) -> int:
    try:
        return int(request.args.get(name, default))
    except Exception:
        return int(default)


@bp.get("/expenses")
@jwt_required()
@require_tenant_admin
def expenses():
    empresa_id = current_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "forbidden"}), 403

    date_from = request.args.get("from")
    date_to = request.args.get("to")

    try:
        data = tenant_expenses_total(int(empresa_id), date_from, date_to)
        return jsonify(data), 200
    except ValueError:
        return jsonify({"error": "invalid_date_format", "hint": "use YYYY-MM-DD"}), 400


@bp.get("/expenses/by-supplier")
@jwt_required()
@require_tenant_admin
def expenses_by_supplier():
    empresa_id = current_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "forbidden"}), 403

    date_from = request.args.get("from")
    date_to = request.args.get("to")
    limit = _int_arg("limit", 20)
    offset = _int_arg("offset", 0)

    try:
        data = tenant_expenses_by_supplier(int(empresa_id), date_from, date_to, limit=limit, offset=offset)
        return jsonify(data), 200
    except ValueError:
        return jsonify({"error": "invalid_date_format", "hint": "use YYYY-MM-DD"}), 400


@bp.get("/suppliers/summary")
@jwt_required()
@require_tenant_admin
def suppliers_summary():
    empresa_id = current_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "forbidden"}), 403

    date_from = request.args.get("from")
    date_to = request.args.get("to")
    limit = _int_arg("limit", 20)
    offset = _int_arg("offset", 0)

    try:
        data = tenant_suppliers_summary(int(empresa_id), date_from, date_to, limit=limit, offset=offset)
        return jsonify(data), 200
    except ValueError:
        return jsonify({"error": "invalid_date_format", "hint": "use YYYY-MM-DD"}), 400


@bp.get("/purchases")
@jwt_required()
@require_tenant_admin
def finance_purchases_list():
    empresa_id = current_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "forbidden"}), 403

    proveedor_id = request.args.get("proveedor_id")
    proveedor_id = int(proveedor_id) if proveedor_id and str(proveedor_id).strip().isdigit() else None

    estado = request.args.get("estado")
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    limit = _int_arg("limit", 20)
    offset = _int_arg("offset", 0)

    try:
        data = tenant_finance_purchases_list(
            int(empresa_id),
            proveedor_id=proveedor_id,
            estado=estado,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        return jsonify(data), 200
    except ValueError:
        return jsonify({"error": "invalid_date_format", "hint": "use YYYY-MM-DD"}), 400


@bp.get("/purchases/<int:compra_id>")
@jwt_required()
@require_tenant_admin
def finance_purchase_detail(compra_id: int):
    empresa_id = current_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "forbidden"}), 403

    data = tenant_finance_purchase_detail(int(empresa_id), int(compra_id))
    if not data:
        return jsonify({"error": "not_found"}), 404

    return jsonify(data), 200


@bp.get("/reports/expenses-series")
@jwt_required()
@require_tenant_admin
def expenses_series():
    empresa_id = current_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "forbidden"}), 403

    date_from = request.args.get("from")
    date_to = request.args.get("to")
    group = (request.args.get("group") or "day").strip().lower()

    try:
        data = tenant_expenses_series(int(empresa_id), date_from, date_to, group=group)
        return jsonify(data), 200
    except ValueError:
        return jsonify({"error": "invalid_date_format", "hint": "use YYYY-MM-DD"}), 400