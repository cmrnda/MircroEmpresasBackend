from app.extensions import db
from app.db.models.cliente import Cliente
from werkzeug.security import generate_password_hash

def list_clients(empresa_id: int, include_inactivos: bool = False):
    """
    Lista clientes por empresa.
    Por defecto SOLO activos (activo=True).
    """
    q = Cliente.query.filter_by(empresa_id=empresa_id)
    if not include_inactivos:
        q = q.filter(Cliente.activo.is_(True))
    return q.order_by(Cliente.cliente_id.desc()).all()

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

def update_client(c: Cliente, payload: dict):
    if payload.get("email") is not None:
        c.email = (payload.get("email") or "").strip().lower()

    if payload.get("nombre_razon") is not None:
        c.nombre_razon = (payload.get("nombre_razon") or "").strip()

    if payload.get("nit_ci") is not None:
        c.nit_ci = payload.get("nit_ci")

    if payload.get("telefono") is not None:
        c.telefono = payload.get("telefono")

    # Esto permite activar/desactivar desde UI si quieren (admin)
    if payload.get("activo") is not None:
        c.activo = bool(payload.get("activo"))

    if payload.get("password"):
        c.password_hash = generate_password_hash(payload.get("password"))

    db.session.commit()
    return c

def delete_client(c: Cliente):
    """
    Eliminación lógica: NO borra de BD.
    Solo marca activo=False.
    """
    c.activo = False
    db.session.commit()
    return c

def get_active_client(empresa_id: int, cliente_id: int):
    return Cliente.query.filter_by(
        empresa_id=empresa_id,
        cliente_id=cliente_id,
        activo=True
    ).first()

def restore_client(c: Cliente):
    c.activo = True
    db.session.commit()
    return c

def list_clients(empresa_id: int, include_inactivos: bool = False):
    q = Cliente.query.filter_by(empresa_id=empresa_id)
    if not include_inactivos:
        q = q.filter(Cliente.activo.is_(True))
    return q.order_by(Cliente.cliente_id.desc()).all()
