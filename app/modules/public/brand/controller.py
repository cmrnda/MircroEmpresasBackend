from flask import Blueprint, jsonify
from app.modules.tenant.settings.repository import EmpresaSettingsRepository
from app.modules.tenant.settings.service import EmpresaSettingsService


bp = Blueprint("public_brand", __name__, url_prefix="/public")


@bp.get("/brand/<int:empresa_id>")
def get_public_brand(empresa_id: int):
    if not empresa_id or empresa_id <= 0:
        return jsonify({"error": "empresa_id_invalid"}), 400

    svc = EmpresaSettingsService(EmpresaSettingsRepository())
    d = svc.get_brand(empresa_id)
    if not d:
        return jsonify({"error": "empresa_not_found"}), 404

    return jsonify(d), 200
