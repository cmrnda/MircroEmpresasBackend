from __future__ import annotations

from flask import Blueprint, jsonify, request, g

from app.modules.tenant.dashboard.service import (
    tenant_dashboard,
    tenant_dashboard_sale_detail,
    tenant_dashboard_purchase_detail,
)

bp = Blueprint("tenant_dashboard", __name__, url_prefix="/tenant/dashboard")


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


@bp.get("")
@bp.get("/")
def dashboard():
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401

    date_from = request.args.get("from")
    date_to = request.args.get("to")
    group = request.args.get("group") or "day"
    limit = _int(request.args.get("limit"), 10)

    return jsonify(tenant_dashboard(empresa_id, date_from, date_to, group, limit)), 200


@bp.get("/sales/<int:venta_id>")
def sale_detail(venta_id: int):
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    res = tenant_dashboard_sale_detail(empresa_id, venta_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200


@bp.get("/purchases/<int:compra_id>")
def purchase_detail(compra_id: int):
    empresa_id = _empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 401
    res = tenant_dashboard_purchase_detail(empresa_id, compra_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify(res), 200
