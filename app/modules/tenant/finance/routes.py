from __future__ import annotations

from flask import Blueprint, jsonify, request, g

from app.modules.tenant.finance.service import (
    tenant_expenses_total,
    tenant_expenses_series,
    tenant_suppliers_summary,
    tenant_finance_purchases_list,
    tenant_finance_purchase_detail,
    tenant_finance_overview,
    tenant_cashflow_series,
    tenant_top_products,
    tenant_top_categories,
    tenant_inventory_alerts,
    tenant_inventory_valuation,
    tenant_finance_sales_list,
    tenant_finance_sale_detail,
)

bp = Blueprint("tenant_finance", __name__, url_prefix="/tenant/finance")


def _int(v, default: int) -> int:
    try:
        return int(v)
    except Exception:
        return default


def _empresa_id() -> int | None:
    eid = getattr(g, "empresa_id", None)
    if eid:
        try:
            return int(eid)
        except Exception:
            return None

    eid = request.headers.get("X-Empresa-Id")
    if eid:
        try:
            return int(eid)
        except Exception:
            return None

    eid = request.args.get("empresa_id")
    if eid:
        try:
            return int(eid)
        except Exception:
            return None

    return None


def _limit_offset(default_limit: int = 20):
    limit = _int(request.args.get("limit"), default_limit)
    offset = _int(request.args.get("offset"), 0)

    if limit <= 0:
        limit = default_limit
    if limit > 200:
        limit = 200
    if offset < 0:
        offset = 0

    return limit, offset


@bp.get("/overview")
def overview():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    return jsonify(tenant_finance_overview(empresa_id, date_from, date_to)), 200


@bp.get("/cashflow-series")
def cashflow_series():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    group = request.args.get("group") or "day"
    return jsonify(tenant_cashflow_series(empresa_id, date_from, date_to, group)), 200


@bp.get("/top-products")
def top_products():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    limit, offset = _limit_offset(10)
    return jsonify(tenant_top_products(empresa_id, date_from, date_to, limit, offset)), 200


@bp.get("/top-categories")
def top_categories():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    limit, offset = _limit_offset(10)
    return jsonify(tenant_top_categories(empresa_id, date_from, date_to, limit, offset)), 200


@bp.get("/inventory-alerts")
def inventory_alerts():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    limit, offset = _limit_offset(20)
    return jsonify(tenant_inventory_alerts(empresa_id, limit, offset)), 200


@bp.get("/inventory-valuation")
def inventory_valuation():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    return jsonify(tenant_inventory_valuation(empresa_id)), 200


@bp.get("/expenses")
def expenses():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    return jsonify(tenant_expenses_total(empresa_id, date_from, date_to)), 200


@bp.get("/expenses-series")
def expenses_series():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    group = request.args.get("group") or "day"
    return jsonify(tenant_expenses_series(empresa_id, date_from, date_to, group)), 200


@bp.get("/suppliers-summary")
def suppliers_summary():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    limit, offset = _limit_offset(10)
    return jsonify(tenant_suppliers_summary(empresa_id, date_from, date_to, limit, offset)), 200


@bp.get("/purchases")
def purchases_list():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401

    proveedor_id = request.args.get("proveedor_id")
    proveedor_id_int = None
    if proveedor_id is not None and str(proveedor_id).strip() != "":
        proveedor_id_int = _int(proveedor_id, 0)
        if proveedor_id_int <= 0:
            proveedor_id_int = None

    estado = request.args.get("estado")
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    limit, offset = _limit_offset(20)

    return (
        jsonify(
            tenant_finance_purchases_list(
                empresa_id=empresa_id,
                proveedor_id=proveedor_id_int,
                estado=estado,
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
            )
        ),
        200,
    )


@bp.get("/purchases/<int:compra_id>")
def purchase_detail(compra_id: int):
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    res = tenant_finance_purchase_detail(empresa_id, compra_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200


@bp.get("/sales")
def sales_list():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401

    cliente_id = request.args.get("cliente_id")
    cliente_id_int = None
    if cliente_id is not None and str(cliente_id).strip() != "":
        cliente_id_int = _int(cliente_id, 0)
        if cliente_id_int <= 0:
            cliente_id_int = None

    estado = request.args.get("estado")
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    limit, offset = _limit_offset(20)

    return (
        jsonify(
            tenant_finance_sales_list(
                empresa_id=empresa_id,
                cliente_id=cliente_id_int,
                estado=estado,
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
            )
        ),
        200,
    )


@bp.get("/sales/<int:venta_id>")
def sale_detail(venta_id: int):
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    res = tenant_finance_sale_detail(empresa_id, venta_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200