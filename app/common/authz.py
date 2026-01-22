from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt


def _claims():
    return get_jwt() or {}


def _actor_type():
    c = _claims()
    if c.get("actor_type"):
        return c.get("actor_type")
    t = c.get("type")
    if t == "client":
        return "client"
    if t in ("platform", "user"):
        return "user"
    return None


def _has_role(role: str):
    roles = _claims().get("roles") or []
    return role in roles


def require_platform_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        c = _claims()
        if _actor_type() != "user":
            return jsonify({"error": "forbidden"}), 403
        if c.get("type") != "platform":
            return jsonify({"error": "forbidden"}), 403
        if not _has_role("PLATFORM_ADMIN"):
            return jsonify({"error": "forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper


def require_tenant_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        c = _claims()
        if _actor_type() != "user":
            return jsonify({"error": "forbidden"}), 403
        if c.get("type") != "user":
            return jsonify({"error": "forbidden"}), 403
        if c.get("empresa_id") is None:
            return jsonify({"error": "forbidden"}), 403
        if not (_has_role("TENANT_ADMIN") or _has_role("SELLER") or _has_role("INVENTORY")):
            return jsonify({"error": "forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper


def require_tenant_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        c = _claims()
        if _actor_type() != "user":
            return jsonify({"error": "forbidden"}), 403
        if c.get("type") != "user":
            return jsonify({"error": "forbidden"}), 403
        if c.get("empresa_id") is None:
            return jsonify({"error": "forbidden"}), 403
        if not _has_role("TENANT_ADMIN"):
            return jsonify({"error": "forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper


def require_seller(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        c = _claims()
        if _actor_type() != "user":
            return jsonify({"error": "forbidden"}), 403
        if c.get("type") != "user":
            return jsonify({"error": "forbidden"}), 403
        if c.get("empresa_id") is None:
            return jsonify({"error": "forbidden"}), 403
        if not (_has_role("SELLER") or _has_role("TENANT_ADMIN")):
            return jsonify({"error": "forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper


def require_client(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        c = _claims()
        if _actor_type() != "client":
            return jsonify({"error": "forbidden"}), 403
        if c.get("empresa_id") is None or c.get("cliente_id") is None:
            return jsonify({"error": "forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper
