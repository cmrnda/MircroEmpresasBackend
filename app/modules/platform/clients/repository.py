from app.extensions import db
from app.database.models.cliente import Cliente, ClienteEmpresa
from app.database.models.empresa import Empresa
from app.security.password import hash_password

def list_clients(empresa_id=None, q=None, include_inactivos=False):
    query = db.session.query(Cliente)
    if not include_inactivos:
        query = query.filter(Cliente.activo.is_(True))
    if q:
        query = query.filter(Cliente.email.ilike(f"%{q}%") | Cliente.nombre_razon.ilike(f"%{q}%"))
    items = query.order_by(Cliente.cliente_id.asc()).all()

    if empresa_id is None:
        return items

    empresa_id = int(empresa_id)
    out = []
    for c in items:
        link = (
            db.session.query(ClienteEmpresa)
            .filter(ClienteEmpresa.empresa_id == empresa_id)
            .filter(ClienteEmpresa.cliente_id == int(c.cliente_id))
            .first()
        )
        if link and (include_inactivos or bool(link.activo)):
            out.append(c)
    return out

def get_client(cliente_id: int):
    return db.session.query(Cliente).filter(Cliente.cliente_id == int(cliente_id)).first()

def create_client(payload: dict):
    c = Cliente(
        email=(payload.get("email") or "").strip(),
        password_hash=hash_password(payload.get("password")),
        nombre_razon=(payload.get("nombre_razon") or "").strip(),
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
    if "activo" in payload and payload.get("activo") is not None:
        c.activo = bool(payload.get("activo"))
    db.session.add(c)
    return c

def soft_delete_client(c: Cliente):
    c.activo = False
    db.session.add(c)
    return c

def link_client_to_tenant(empresa_id: int, cliente_id: int):
    empresa_id = int(empresa_id)
    cliente_id = int(cliente_id)
    row = (
        db.session.query(ClienteEmpresa)
        .filter_by(empresa_id=empresa_id, cliente_id=cliente_id)
        .first()
    )
    if row:
        row.activo = True
        db.session.add(row)
        return row
    row = ClienteEmpresa(empresa_id=empresa_id, cliente_id=cliente_id, activo=True)
    db.session.add(row)
    return row

def unlink_client_from_tenant(empresa_id: int, cliente_id: int):
    row = (
        db.session.query(ClienteEmpresa)
        .filter_by(empresa_id=int(empresa_id), cliente_id=int(cliente_id))
        .first()
    )
    if not row:
        return None
    row.activo = False
    db.session.add(row)
    return row

def list_tenants_for_client(cliente_id: int):
    rows = (
        db.session.query(ClienteEmpresa.empresa_id, Empresa.nombre, ClienteEmpresa.activo)
        .join(Empresa, Empresa.empresa_id == ClienteEmpresa.empresa_id)
        .filter(ClienteEmpresa.cliente_id == int(cliente_id))
        .order_by(ClienteEmpresa.empresa_id.asc())
        .all()
    )
    return [{"empresa_id": int(r[0]), "nombre": r[1], "activo": bool(r[2])} for r in rows]
