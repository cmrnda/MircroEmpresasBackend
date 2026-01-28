# app/modules/tenant/pos/routes.py

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from io import BytesIO

from app.common.current import current_empresa_id
from app.common.authz import require_tenant_admin
from app.modules.tenant.pos.service import (
    pos_lookup_client,
    pos_create_client,
    pos_create_sale,
    tenant_generate_sale_receipt_pdf,
)

bp = Blueprint("tenant_pos_api", __name__, url_prefix="/tenant/pos")


@bp.get("/<int:empresa_id>/clients/lookup")
@jwt_required()
def lookup_client(empresa_id: int):
    token_empresa_id = int(current_empresa_id())
    if empresa_id != token_empresa_id:
        return jsonify({"error": "forbidden_empresa"}), 403

    nit_ci = (request.args.get("nit_ci") or "").strip() or None
    data = pos_lookup_client(empresa_id, nit_ci)

    if not data:
        return jsonify({"found": False, "client": None}), 200

    return jsonify({"found": True, "client": data}), 200


@bp.post("/<int:empresa_id>/clients")
@jwt_required()
def create_client(empresa_id: int):
    token_empresa_id = int(current_empresa_id())
    if empresa_id != token_empresa_id:
        return jsonify({"error": "forbidden_empresa"}), 403

    payload = request.get_json(silent=True) or {}
    data, err = pos_create_client(empresa_id, payload)

    if err:
        code = 409 if err in ("email_taken",) else 400 if err in ("invalid_payload",) else 500
        return jsonify({"error": err}), code

    return jsonify(data), 201


@bp.post("/<int:empresa_id>/sales")
@jwt_required()
def create_sale(empresa_id: int):
    token_empresa_id = int(current_empresa_id())
    if empresa_id != token_empresa_id:
        return jsonify({"error": "forbidden_empresa"}), 403

    payload = request.get_json(silent=True) or {}
    data, err = pos_create_sale(empresa_id, payload)

    if err:
        code = 409 if err in ("stock_insuficiente", "conflict") else 404 if err in ("cliente_not_found",) else 400
        return jsonify({"error": err}), code

    return jsonify(data), 201


@bp.get("/sales/<int:venta_id>/receipt.pdf")
@jwt_required()
@require_tenant_admin
def download_sale_receipt_route(venta_id: int):
    empresa_id = int(current_empresa_id())

    pdf_bytes, err = tenant_generate_sale_receipt_pdf(empresa_id, venta_id)
    if err:
        code = 404 if err == "not_found" else 400
        return jsonify({"error": err}), code

    bio = BytesIO(pdf_bytes)
    bio.seek(0)

    return send_file(
        bio,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"recibo_venta_{venta_id}.pdf",
    )
