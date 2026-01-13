from flask import g, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt

PUBLIC_PREFIXES = (
    "/auth/",
    "/health",
    "/static/",
)


def init_tenant_context(app):
    @app.before_request
    def tenant_context():
        if request.method == "OPTIONS":
            return

        path = request.path or ""
        if path == "/" or any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return

        verify_jwt_in_request()
        claims = get_jwt()

        g.usuario_id = claims.get("usuario_id")
        g.scope = claims.get("scope")
        g.empresa_id = claims.get("empresa_id")
        g.roles = claims.get("roles", [])
        g.primary_role = claims.get("primary_role")
