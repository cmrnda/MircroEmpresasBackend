from datetime import datetime, timezone
from app.extensions import db
from app.database.models.usuario import (
    Usuario,
    UsuarioEmpresa,
    UsuarioAdminEmpresa,
    UsuarioVendedor,
    UsuarioEncargadoInventario,
)
from app.security.password import hash_password

def list_users(empresa_id: int, q=None, include_inactivos=False):
    query = (
        db.session.query(Usuario, UsuarioEmpresa)
        .join(UsuarioEmpresa, UsuarioEmpresa.usuario_id == Usuario.usuario_id)
        .filter(UsuarioEmpresa.empresa_id == int(empresa_id))
    )
    if not include_inactivos:
        query = query.filter(UsuarioEmpresa.activo.is_(True)).filter(Usuario.activo.is_(True))
    if q:
        qq = f"%{q}%"
        query = query.filter(Usuario.email.ilike(qq))
    return query.order_by(Usuario.usuario_id.asc()).all()

def get_usuario(usuario_id: int):
    return db.session.query(Usuario).filter(Usuario.usuario_id == int(usuario_id)).first()

def get_membership(empresa_id: int, usuario_id: int):
    return (
        db.session.query(UsuarioEmpresa)
        .filter(UsuarioEmpresa.empresa_id == int(empresa_id))
        .filter(UsuarioEmpresa.usuario_id == int(usuario_id))
        .first()
    )

def get_roles(empresa_id: int, usuario_id: int):
    roles = []
    if db.session.query(UsuarioAdminEmpresa).filter_by(empresa_id=int(empresa_id), usuario_id=int(usuario_id)).first():
        roles.append("TENANT_ADMIN")
    if db.session.query(UsuarioVendedor).filter_by(empresa_id=int(empresa_id), usuario_id=int(usuario_id)).first():
        roles.append("SELLER")
    if db.session.query(UsuarioEncargadoInventario).filter_by(empresa_id=int(empresa_id), usuario_id=int(usuario_id)).first():
        roles.append("INVENTORY")
    return roles

def create_user(email: str, password: str):
    u = Usuario(email=email, password_hash=hash_password(password), activo=True)
    db.session.add(u)
    db.session.flush()
    return u

def add_membership(empresa_id: int, usuario_id: int):
    row = get_membership(empresa_id, usuario_id)
    if row:
        row.activo = True
        db.session.add(row)
        return row
    row = UsuarioEmpresa(empresa_id=int(empresa_id), usuario_id=int(usuario_id), activo=True)
    db.session.add(row)
    return row

def set_membership_active(row: UsuarioEmpresa, activo: bool):
    row.activo = bool(activo)
    db.session.add(row)
    return row

def set_password(u: Usuario, new_password: str):
    u.password_hash = hash_password(new_password)
    db.session.add(u)
    return u

def set_roles(empresa_id: int, usuario_id: int, roles: list[str]):
    wanted = set([r.strip().upper() for r in (roles or []) if isinstance(r, str) and r.strip()])
    current = {
        "TENANT_ADMIN": db.session.query(UsuarioAdminEmpresa).filter_by(empresa_id=int(empresa_id), usuario_id=int(usuario_id)).first(),
        "SELLER": db.session.query(UsuarioVendedor).filter_by(empresa_id=int(empresa_id), usuario_id=int(usuario_id)).first(),
        "INVENTORY": db.session.query(UsuarioEncargadoInventario).filter_by(empresa_id=int(empresa_id), usuario_id=int(usuario_id)).first(),
    }

    if "TENANT_ADMIN" in wanted and not current["TENANT_ADMIN"]:
        db.session.add(UsuarioAdminEmpresa(empresa_id=int(empresa_id), usuario_id=int(usuario_id)))
    if "TENANT_ADMIN" not in wanted and current["TENANT_ADMIN"]:
        db.session.delete(current["TENANT_ADMIN"])

    if "SELLER" in wanted and not current["SELLER"]:
        db.session.add(UsuarioVendedor(empresa_id=int(empresa_id), usuario_id=int(usuario_id)))
    if "SELLER" not in wanted and current["SELLER"]:
        db.session.delete(current["SELLER"])

    if "INVENTORY" in wanted and not current["INVENTORY"]:
        db.session.add(UsuarioEncargadoInventario(empresa_id=int(empresa_id), usuario_id=int(usuario_id)))
    if "INVENTORY" not in wanted and current["INVENTORY"]:
        db.session.delete(current["INVENTORY"])

def touch_login(u: Usuario):
    u.ultimo_login = datetime.now(timezone.utc)
    db.session.add(u)
    return u
