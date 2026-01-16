from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.modules.empresa_config.service import EmpresaConfigService

_service = EmpresaConfigService()

bp = Blueprint("empresa_config", __name__, url_prefix="/empresa/config")

def _empresa_id_from_request() -> int:
    # Regla que estás usando en el proyecto: header X-Empresa-Id (y si no hay, 400)
    empresa_id = request.headers.get("X-Empresa-Id")
    if not empresa_id:
        raise ValueError("EMPRESA_ID_REQUIRED")
    return int(empresa_id)

@bp.get("")
@jwt_required()

def get_empresa_config():
    try:
        empresa_id = _empresa_id_from_request()
        return jsonify({"data": _service.get_config(empresa_id)}), 200
    except ValueError as e:
        if str(e) == "EMPRESA_ID_REQUIRED":
            return jsonify({"error": "empresa_id required"}), 400
        return jsonify({"error": str(e).lower()}), 400

@bp.put("")
@jwt_required()

def put_empresa_config():
    data = request.get_json(silent=True) or {}
    try:
        empresa_id = _empresa_id_from_request()
        updated = _service.update_config(empresa_id, data)
        return jsonify({"data": updated}), 200
    except ValueError as e:
        if str(e) == "EMPRESA_ID_REQUIRED":
            return jsonify({"error": "empresa_id required"}), 400
        if str(e) == "MONEDA_INVALID":
            return jsonify({"error": "moneda invalid"}), 400
        if str(e) == "TASA_INVALID":
            return jsonify({"error": "tasa_impuesto invalid"}), 400
        if str(e) == "TASA_OUT_OF_RANGE":
            return jsonify({"error": "tasa_impuesto out of range (0..100)"}), 400
        return jsonify({"error": str(e).lower()}), 400
