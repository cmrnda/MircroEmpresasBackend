from app.extensions import db
from app.database.models.cliente import Cliente, ClienteEmpresa
from app.security.password import hash_password

def list_clients_for_tenant(empresa_id: int, q=None, include_inactivos=False):
    query = (
        db.session.query(Cliente)
        .join(ClienteEmpresa, ClienteEmpresa.cliente_id == Cliente.cliente_id)
        .filter(ClienteEmpresa.empresa_id == int(empresa_id))
    )
    if not include_inactivos:
        query = query.filter(ClienteEmpresa.activo.is_(True)).filter(Cliente.activo.is_(True))
    if q:
        qq = f"%{q}%"
        query = query.filter(Cliente.email.ilike(qq) | Cliente.nombre_razon.ilike(qq))
    return query.order_by(Cliente.cliente_id.asc()).all()

def get_link(empresa_id: int, cliente_id: int):
    return (
        db.session.query(ClienteEmpresa)
        .filter(ClienteEmpresa.empresa_id == int(empresa_id))
        .filter(ClienteEmpresa.cliente_id == int(cliente_id))
        .first()
    )

def get_client(cliente_id: int):
    return db.session.query(Cliente).filter(Cliente.cliente_id == int(cliente_id)).first()

def create_client(payload: dict):
    c = Cliente(
        email=str(payload.get("email")).strip(),
        password_hash=hash_password(payload.get("password")),
        nombre_razon=str(payload.get("nombre_razon")).strip(),
        nit_ci=(payload.get("nit_ci") or "").strip() or None,
        telefono=(payload.get("telefono") or "").strip() or None,
        activo=True,
    )
    db.session.add(c)
    db.session.flush()
    return c

def update_client(c: Cliente, payload: dict):
    if "email" in payload and payload.get("email") is not None:
        c.email = str(payload.get("email")).strip()
    if "nombre_razon" in payload and payload.get("nombre_razon") is not None:
        c.nombre_razon = str(payload.get("nombre_razon")).strip()
    if "nit_ci" in payload:
        c.nit_ci = (payload.get("nit_ci") or "").strip() or None
    if "telefono" in payload:
        c.telefono = (payload.get("telefono") or "").strip() or None
    db.session.add(c)
    return c

def link_client(empresa_id: int, cliente_id: int):
    row = get_link(empresa_id, cliente_id)
    if row:
        row.activo = True
        db.session.add(row)
        return row
    row = ClienteEmpresa(empresa_id=int(empresa_id), cliente_id=int(cliente_id), activo=True)
    db.session.add(row)
    return row

def unlink_client(empresa_id: int, cliente_id: int):
    row = get_link(empresa_id, cliente_id)
    if not row:
        return None
    row.activo = False
    db.session.add(row)
    return row
