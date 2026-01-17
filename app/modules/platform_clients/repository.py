from app.db.models.cliente import Cliente
from app.extensions import db
from werkzeug.security import generate_password_hash


def list_platform_clients(empresa_id: int | None = None, include_inactivos: bool = False):
    q = Cliente.query
    if empresa_id is not None:
        q = q.filter(Cliente.empresa_id == empresa_id)
    if not include_inactivos:
        q = q.filter(Cliente.activo.is_(True))
    return q.order_by(Cliente.cliente_id.desc()).all()


def get_client_by_id(cliente_id: int):
    return Cliente.query.filter_by(cliente_id=cliente_id).first()


def get_client_by_empresa(empresa_id: int, cliente_id: int):
    return Cliente.query.filter_by(empresa_id=empresa_id, cliente_id=cliente_id).first()


def create_client_for_empresa(empresa_id: int, payload: dict):
    email = (payload.get("email") or "").strip().lower()

    c = Cliente(
        empresa_id=empresa_id,
        email=email,
        password_hash=generate_password_hash(payload.get("password")),
        nombre_razon=(payload.get("nombre_razon") or "").strip(),
        nit_ci=payload.get("nit_ci"),
        telefono=payload.get("telefono"),
        activo=True,
    )
    db.session.add(c)
    db.session.commit()
    return c


def update_client_model(c: Cliente, payload: dict):
    if payload.get("email") is not None:
        c.email = (payload.get("email") or "").strip().lower()
    if payload.get("nombre_razon") is not None:
        c.nombre_razon = (payload.get("nombre_razon") or "").strip()
    if payload.get("nit_ci") is not None:
        c.nit_ci = payload.get("nit_ci")
    if payload.get("telefono") is not None:
        c.telefono = payload.get("telefono")
    if payload.get("password"):
        c.password_hash = generate_password_hash(payload.get("password"))

    db.session.commit()
    return c


def soft_delete_client(c: Cliente):
    c.activo = False
    db.session.commit()
    return c


def restore_client(c: Cliente):
    c.activo = True
    db.session.commit()
    return c
