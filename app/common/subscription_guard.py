from datetime import date

from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

from app.db.models.empresa import Empresa
from app.db.models.suscripcion import Suscripcion
from app.extensions import db

ALLOW_PREFIXES = (
    "/auth",
    "/tenant/subscription",
)


def _latest_subscription(empresa_id: int):
    return (
        Suscripcion.query
        .filter(Suscripcion.empresa_id == empresa_id)
        .order_by(Suscripcion.suscripcion_id.desc())
        .first()
    )


def _is_active(s: Suscripcion | None, today: date) -> bool:
    return bool(s and s.estado == "ACTIVA" and s.fin and s.fin >= today)


def register_subscription_guard(app):
    @app.before_request
    def _guard():
        if request.method == "OPTIONS":
            return None

        path = request.path or ""

        if any(path.startswith(p) for p in ALLOW_PREFIXES):
            return None

        if not path.startswith("/tenant/"):
            return None

        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            return None

        claims = get_jwt() or {}
        empresa_id = claims.get("empresa_id")
        if not empresa_id:
            return None

        empresa_id = int(empresa_id)

        e = Empresa.query.filter_by(empresa_id=empresa_id).first()
        if not e:
            return jsonify({"error": "empresa_not_found"}), 404

        if e.estado == "SUSPENDIDA":
            return jsonify({"error": "subscription_required"}), 402

        today = date.today()
        s = _latest_subscription(empresa_id)

        if _is_active(s, today):
            return None

        e.estado = "SUSPENDIDA"
        if s and s.estado != "CANCELADA":
            s.estado = "VENCIDA"
        db.session.commit()

        return jsonify({"error": "subscription_required"}), 402
