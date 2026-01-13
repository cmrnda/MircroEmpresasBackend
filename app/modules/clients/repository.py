from app.extensions import db
from app.db.models.cliente import Cliente
from werkzeug.security import generate_password_hash

def list_clients(empresa_id):
    return Cliente.query.filter_by(empresa_id=empresa_id).order_by(Cliente.cliente_id.desc()).all()

def get_client(empresa_id, cliente_id):
    return Cliente.query.filter_by(empresa_id=empresa_id, cliente_id=cliente_id).first()

def create_client(empresa_id, payload):
    c = Cliente(
        empresa_id=empresa_id,
        email=payload.get("email"),
        password_hash=generate_password_hash(payload.get("password")),
        nombre_razon=payload.get("nombre_razon"),
        nit_ci=payload.get("nit_ci"),
        telefono=payload.get("telefono"),
    )
    db.session.add(c)
    db.session.commit()
    return c

def update_client(c, payload):
    if payload.get("email") is not None:
        c.email = payload.get("email")
    if payload.get("nombre_razon") is not None:
        c.nombre_razon = payload.get("nombre_razon")
    if payload.get("nit_ci") is not None:
        c.nit_ci = payload.get("nit_ci")
    if payload.get("telefono") is not None:
        c.telefono = payload.get("telefono")
    if payload.get("activo") is not None:
        c.activo = bool(payload.get("activo"))
    if payload.get("password"):
        c.password_hash = generate_password_hash(payload.get("password"))
    db.session.commit()
    return c

def delete_client(c):
    db.session.delete(c)
    db.session.commit()
