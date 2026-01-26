from io import BytesIO
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from app.common.authz import require_tenant_admin
from app.common.current import current_empresa_id, current_usuario_id
from app.extensions import db
from app.database.models.proveedor import Proveedor
from app.database.models.producto import Producto
from app.modules.tenant.purchases.service import (
    tenant_list_purchases,
    tenant_get_purchase,
    tenant_create_purchase,
    tenant_add_purchase_item,
    tenant_update_purchase_item,
    tenant_delete_purchase_item,
    tenant_receive_purchase,
    tenant_cancel_purchase,
)
from app.modules.tenant.purchases.pdf import build_purchase_pdf

bp = Blueprint("tenant_purchases_api", __name__, url_prefix="/tenant/purchases")

@bp.get("")
@jwt_required()
@require_tenant_admin
def list_purchases():
    empresa_id = int(current_empresa_id())
    proveedor_id = request.args.get("proveedor_id")
    proveedor_id = int(proveedor_id) if proveedor_id and str(proveedor_id).strip().isdigit() else None
    estado = (request.args.get("estado") or "").strip() or None
    return jsonify({"items": tenant_list_purchases(empresa_id, proveedor_id=proveedor_id, estado=estado)}), 200

@bp.get("/<int:compra_id>")
@jwt_required()
@require_tenant_admin
def get_purchase(compra_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_get_purchase(empresa_id, compra_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data), 200

@bp.post("")
@jwt_required()
@require_tenant_admin
def create_purchase():
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_create_purchase(empresa_id, payload)
    if err:
        code = 409 if err == "conflict" else 400
        return jsonify({"error": err}), code
    return jsonify(data), 201

@bp.post("/<int:compra_id>/items")
@jwt_required()
@require_tenant_admin
def add_item(compra_id: int):
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_add_purchase_item(empresa_id, compra_id, payload)
    if err:
        code = 404 if err in ("not_found",) else 409 if err in ("invalid_state", "conflict") else 400
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.put("/<int:compra_id>/items/<int:compra_detalle_id>")
@jwt_required()
@require_tenant_admin
def update_item(compra_id: int, compra_detalle_id: int):
    empresa_id = int(current_empresa_id())
    payload = request.get_json(silent=True) or {}
    data, err = tenant_update_purchase_item(empresa_id, compra_id, compra_detalle_id, payload)
    if err:
        code = 404 if err in ("not_found", "not_found_item") else 409 if err in ("invalid_state", "conflict") else 400
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.delete("/<int:compra_id>/items/<int:compra_detalle_id>")
@jwt_required()
@require_tenant_admin
def delete_item(compra_id: int, compra_detalle_id: int):
    empresa_id = int(current_empresa_id())
    data, err = tenant_delete_purchase_item(empresa_id, compra_id, compra_detalle_id)
    if err:
        code = 404 if err in ("not_found", "not_found_item") else 409
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.post("/<int:compra_id>/receive")
@jwt_required()
@require_tenant_admin
def receive_purchase(compra_id: int):
    empresa_id = int(current_empresa_id())
    usuario_id = int(current_usuario_id())
    data, err = tenant_receive_purchase(empresa_id, compra_id, usuario_id)
    if err:
        code = 404 if err == "not_found" else 409
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.post("/<int:compra_id>/cancel")
@jwt_required()
@require_tenant_admin
def cancel_purchase(compra_id: int):
    empresa_id = int(current_empresa_id())
    data, err = tenant_cancel_purchase(empresa_id, compra_id)
    if err:
        code = 404 if err == "not_found" else 409
        return jsonify({"error": err}), code
    return jsonify(data), 200

@bp.get("/<int:compra_id>/pdf")
@jwt_required()
@require_tenant_admin
def purchase_pdf(compra_id: int):
    empresa_id = int(current_empresa_id())
    data = tenant_get_purchase(empresa_id, compra_id)
    if not data:
        return jsonify({"error": "not_found"}), 404

    proveedor_id = int(data.get("proveedor_id") or 0)
    sup = (
        db.session.query(Proveedor)
        .filter(Proveedor.empresa_id == int(empresa_id))
        .filter(Proveedor.proveedor_id == int(proveedor_id))
        .first()
    )
    supplier_name = sup.nombre if sup else f"#{proveedor_id}"

    producto_ids = []
    for d in data.get("detalle", []) or []:
        try:
            producto_ids.append(int(d.get("producto_id") or 0))
        except Exception:
            pass

    product_map = {}
    if producto_ids:
        rows = (
            db.session.query(Producto)
            .filter(Producto.empresa_id == int(empresa_id))
            .filter(Producto.producto_id.in_(list(set(producto_ids))))
            .all()
        )
        for p in rows:
            cod = (getattr(p, "codigo", None) or "").strip()
            desc = (getattr(p, "descripcion", None) or "").strip()
            product_map[int(p.producto_id)] = f"{cod} - {desc}".strip(" -")

    pdf_bytes = build_purchase_pdf(data, supplier_name, product_map)
    f = BytesIO(pdf_bytes)

    return send_file(
        f,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"purchase_{compra_id}.pdf",
    )
