from flask_jwt_extended import get_jwt

def current_empresa_id():
    return (get_jwt() or {}).get("empresa_id")

def current_usuario_id():
    return (get_jwt() or {}).get("usuario_id")

def current_cliente_id():
    return (get_jwt() or {}).get("cliente_id")
