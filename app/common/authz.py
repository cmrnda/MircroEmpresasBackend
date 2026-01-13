from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import verify_jwt_in_request


def require_scope(scope: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if getattr(g, "scope", None) != scope:
                return jsonify({"error": "forbidden_scope"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def require_empresa_id(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        empresa_id = getattr(g, "empresa_id", None)
        if empresa_id is None:
            return jsonify({"error": "empresa_required"}), 400
        return fn(*args, **kwargs)

    return wrapper


def require_role(role: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            roles = getattr(g, "roles", []) or []
            if role not in roles:
                return jsonify({"error": "forbidden_role"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
