from flask import jsonify, g
from . import system_bp

@system_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

@system_bp.get("/me")
def me():
    # Tu before_request ya hizo verify_jwt_in_request() y cargó g.*
    return jsonify({
        "empresa_id": getattr(g, "empresa_id", None),
        "usuario_id": getattr(g, "usuario_id", None),
        "roles": getattr(g, "roles", []),
    }), 200
