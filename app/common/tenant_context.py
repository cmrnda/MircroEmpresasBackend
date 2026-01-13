from flask_jwt_extended import get_jwt

def current_empresa_id():
    claims = get_jwt()
    return claims.get("empresa_id")
