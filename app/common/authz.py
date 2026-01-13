from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def require_types(*allowed_types):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            t = claims.get("type")
            if t not in allowed_types:
                return jsonify({"error": "forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return deco

def require_roles(*required_roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            roles = claims.get("roles") or []
            if not set(required_roles).intersection(set(roles)):
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
