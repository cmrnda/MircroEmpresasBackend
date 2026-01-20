from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def _get_claims():
    claims = get_jwt()
    return claims if isinstance(claims, dict) else {}


def _get_type(claims: dict):
    t = claims.get("type")
    return t if isinstance(t, str) else None


def _get_roles(claims: dict):
    roles = claims.get("roles")

    if roles is None:
        return set()

    if isinstance(roles, str):
        roles = roles.strip()
        return {roles} if roles else set()

    if isinstance(roles, list):
        out = set()
        for r in roles:
            if isinstance(r, str):
                rr = r.strip()
                if rr:
                    out.add(rr)
        return out

    return set()


def require_types(*allowed_types):
    allowed = set([t for t in allowed_types if isinstance(t, str) and t.strip()])

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = _get_claims()
            t = _get_type(claims)
            if t not in allowed:
                return jsonify({"error": "forbidden"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return deco


def require_roles(*required_roles):
    required = set([r for r in required_roles if isinstance(r, str) and r.strip()])

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = _get_claims()
            roles = _get_roles(claims)
            if not roles.intersection(required):
                return jsonify({"error": "forbidden"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return deco


def require_platform_admin(fn):
    return require_types("platform")(require_roles("PLATFORM_ADMIN")(fn))


def require_tenant_admin(fn):
    return require_types("user")(require_roles("TENANT_ADMIN")(fn))


def require_tenant_user(fn):
    return require_types("user")(fn)


def require_client(fn):
    return require_types("client")(fn)


def require_seller(fn):
    return require_types("user")(require_roles("SELLER", "TENANT_ADMIN")(fn))
