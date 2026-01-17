from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.common.authz import require_platform_admin
from app.modules.platform_clients.service import (
    platform_list_clients,
    platform_get_client,
    platform_list_clients_by_empresa,
    platform_create_client,
    platform_update_client,
    platform_delete_client,
    platform_restore_client,
)

bp = Blueprint("platform_clients", __name__, url_prefix="/platform")


# 1) Lista global + filtro por empresa
@bp.get("/clients")
@jwt_required()
@require_platform_admin
def list_all_clients():
    empresa_id_raw = request.args.get("empresa_id")
    empresa_id = int(empresa_id_raw) if empresa_id_raw else None
    include_inactivos = request.args.get("include_inactivos") in ("1", "true", "True")

    return jsonify({"data": platform_list_clients(empresa_id, include_inactivos)}), 200


# (Opcional) detalle global por id
@bp.get("/clients/<int:cliente_id>")
@jwt_required()
@require_platform_admin
def get_client(cliente_id):
    res = platform_get_client(cliente_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"data": res}), 200


# 2) Lista por empresa (explícito)
@bp.get("/empresas/<int:empresa_id>/clients")
@jwt_required()
@require_platform_admin
def list_clients_by_empresa(empresa_id):
    include_inactivos = request.args.get("include_inactivos") in ("1", "true", "True")
    return jsonify({"data": platform_list_clients_by_empresa(empresa_id, include_inactivos)}), 200


# 3) Crear por empresa
@bp.post("/empresas/<int:empresa_id>/clients")
@jwt_required()
@require_platform_admin
def create_client(empresa_id):
    data = request.get_json(silent=True) or {}
    res, err = platform_create_client(empresa_id, data)
    if err:
        return jsonify({"error": err}), 409 if err == "conflict" else 400
    return jsonify({"data": res}), 201


# 4) Update por empresa
@bp.put("/empresas/<int:empresa_id>/clients/<int:cliente_id>")
@jwt_required()
@require_platform_admin
def update_client(empresa_id, cliente_id):
    data = request.get_json(silent=True) or {}
    res = platform_update_client(empresa_id, cliente_id, data)
    if not res:
        return jsonify({"error": "not_found"}), 404
    if isinstance(res, dict) and res.get("error") == "conflict":
        return jsonify(res), 409
    return jsonify({"data": res}), 200


# 5) Soft delete por empresa
@bp.delete("/empresas/<int:empresa_id>/clients/<int:cliente_id>")
@jwt_required()
@require_platform_admin
def delete_client(empresa_id, cliente_id):
    ok = platform_delete_client(empresa_id, cliente_id)
    if not ok:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"ok": True}), 200


# 6) Restore por empresa
@bp.patch("/empresas/<int:empresa_id>/clients/<int:cliente_id>/restore")
@jwt_required()
@require_platform_admin
def restore_client(empresa_id, cliente_id):
    res = platform_restore_client(empresa_id, cliente_id)
    if not res:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"data": res}), 200
