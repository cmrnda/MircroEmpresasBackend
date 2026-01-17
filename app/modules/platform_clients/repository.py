from sqlalchemy import or_
from werkzeug.security import generate_password_hash

from app.db.models.cliente import Cliente
from app.extensions import db


def platform_list_clients_repo(empresa_id: int | None, q: str | None, include_inactivos: bool):
    query = Cliente.query
    if empresa_id:
        query = query.filter(Cliente.empresa_id == empresa_id)
    if not include_inactivos:
        query = query.filter(Cliente.activo.is_(True))
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Cliente.email.ilike(term),
                Cliente.nombre_razon.ilike(term),
                Cliente.nit_ci.ilike(term),
                Cliente.telefono.ilike(term),
            )
        )
    return query.order_by(Cliente.cliente_id.desc()).all()


def platform_get_client_repo(cliente_id: int):
    return Cliente.query.filter_by(cliente_id=cliente_id).first()


def platform_create_client_repo(empresa_id: int, payload: dict):
    c = Cliente(
        empresa_id=empresa_id,
        email=(payload.get("email") or "").strip().lower(),
        password_hash=generate_password_hash(payload.get("password")),
        nombre_razon=(payload.get("nombre_razon") or "").strip(),
        nit_ci=payload.get("nit_ci"),
        telefono=payload.get("telefono"),
    )
    db.session.add(c)
    db.session.commit()
    return c


def platform_update_client_repo(c: Cliente, payload: dict):
    if payload.get("empresa_id") is not None:
        c.empresa_id = int(payload.get("empresa_id"))

    if payload.get("email") is not None:
        c.email = (payload.get("email") or "").strip().lower()

    if payload.get("nombre_razon") is not None:
        c.nombre_razon = (payload.get("nombre_razon") or "").strip()

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


def platform_delete_client_repo(cliente_id: int):
    c = platform_get_client_repo(cliente_id)
    if not c:
        return False
    c.activo = False
    db.session.commit()
    return True


def platform_restore_client_repo(c: Cliente):
    c.activo = True
    db.session.commit()
    return c
