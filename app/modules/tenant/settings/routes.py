from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.modules.tenant.settings.repository import EmpresaSettingsRepository
from app.modules.tenant.settings.service import EmpresaSettingsService


bp = Blueprint("tenant_settings", __name__, url_prefix="/tenant")


def _current_empresa_id() -> int | None:
    claims = {}
    try:
        claims = get_jwt() or {}
    except Exception:
        claims = {}

    eid = claims.get("empresa_id") or claims.get("empresaId")
    if eid:
        try:
            n = int(eid)
            return n if n > 0 else None
        except Exception:
            return None

    ident = None
    try:
        ident = get_jwt_identity()
    except Exception:
        ident = None

    if isinstance(ident, dict):
        eid2 = ident.get("empresa_id") or ident.get("empresaId")
        if eid2:
            try:
                n = int(eid2)
                return n if n > 0 else None
            except Exception:
                return None

    return None


def _is_tenant_user() -> bool:
    claims = {}
    try:
        claims = get_jwt() or {}
    except Exception:
        claims = {}
    t = claims.get("type") or claims.get("tipo")
    return str(t or "").lower() in ("user", "tenant")


@bp.get("/settings")
@jwt_required()
def get_settings():
    if not _is_tenant_user():
        return jsonify({"error": "forbidden"}), 403

    empresa_id = _current_empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 400

    svc = EmpresaSettingsService(EmpresaSettingsRepository())
    d = svc.get_settings(empresa_id)
    if not d:
        return jsonify({"error": "empresa_not_found"}), 404

    return jsonify(d), 200


@bp.put("/settings")
@jwt_required()
def put_settings():
    if not _is_tenant_user():
        return jsonify({"error": "forbidden"}), 403

    empresa_id = _current_empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 400

    payload = request.get_json(silent=True) or {}
    allow = {"moneda", "tasa_impuesto", "logo_url", "image_url", "descripcion"}
    clean = {k: payload.get(k) for k in payload.keys() if k in allow}

    svc = EmpresaSettingsService(EmpresaSettingsRepository())
    d = svc.update_settings(empresa_id, clean)
    if not d:
        return jsonify({"error": "empresa_not_found"}), 404

    return jsonify(d), 200


@bp.get("/brand")
@jwt_required()
def get_brand():
    if not _is_tenant_user():
        return jsonify({"error": "forbidden"}), 403

    empresa_id = _current_empresa_id()
    if not empresa_id:
        return jsonify({"error": "empresa_id_missing"}), 400

    svc = EmpresaSettingsService(EmpresaSettingsRepository())
    d = svc.get_brand(empresa_id)
    if not d:
        return jsonify({"error": "empresa_not_found"}), 404

    return jsonify(d), 200
