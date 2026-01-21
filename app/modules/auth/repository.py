from datetime import datetime, timezone
from app.extensions import db
from app.database.models.usuario import (
    Usuario,
    UsuarioAdminPlataforma,
    UsuarioEmpresa,
    UsuarioAdminEmpresa,
    UsuarioVendedor,
    UsuarioEncargadoInventario,
)
from app.database.models.cliente import Cliente, ClienteEmpresa
from app.database.models.empresa import Empresa
from app.database.models.token_blocklist import TokenBlocklist

def get_usuario_by_email(email: str):
    return db.session.query(Usuario).filter(Usuario.email == str(email)).first()

def get_cliente_by_email(email: str):
    return db.session.query(Cliente).filter(Cliente.email == str(email)).first()

def is_platform_admin(usuario_id: int):
    return db.session.query(UsuarioAdminPlataforma).filter(UsuarioAdminPlataforma.usuario_id == int(usuario_id)).first() is not None

def get_empresa(empresa_id: int):
    return db.session.query(Empresa).filter(Empresa.empresa_id == int(empresa_id)).first()

def get_membership(empresa_id: int, usuario_id: int):
    return (
        db.session.query(UsuarioEmpresa)
        .filter(UsuarioEmpresa.empresa_id == int(empresa_id))
        .filter(UsuarioEmpresa.usuario_id == int(usuario_id))
        .first()
    )

def get_tenant_roles(empresa_id: int, usuario_id: int):
    roles = []
    if db.session.query(UsuarioAdminEmpresa).filter_by(empresa_id=int(empresa_id), usuario_id=int(usuario_id)).first():
        roles.append("TENANT_ADMIN")
    if db.session.query(UsuarioVendedor).filter_by(empresa_id=int(empresa_id), usuario_id=int(usuario_id)).first():
        roles.append("SELLER")
    if db.session.query(UsuarioEncargadoInventario).filter_by(empresa_id=int(empresa_id), usuario_id=int(usuario_id)).first():
        roles.append("INVENTORY")
    return roles

def get_cliente_empresa_link(empresa_id: int, cliente_id: int):
    return (
        db.session.query(ClienteEmpresa)
        .filter(ClienteEmpresa.empresa_id == int(empresa_id))
        .filter(ClienteEmpresa.cliente_id == int(cliente_id))
        .first()
    )

def touch_usuario_login(u: Usuario):
    u.ultimo_login = datetime.now(timezone.utc)
    db.session.add(u)
    return u

def touch_cliente_login(c: Cliente):
    c.ultimo_login = datetime.now(timezone.utc)
    db.session.add(c)
    return c

def revoke_jti(jti: str, usuario_id: int | None):
    row = TokenBlocklist(jti=str(jti), usuario_id=int(usuario_id) if usuario_id is not None else None)
    db.session.add(row)
    return row
