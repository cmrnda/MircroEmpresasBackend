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
from app.database.models.empresa import Empresa
from app.database.models.cliente import Cliente, ClienteEmpresa

def get_usuario_by_email(email):
    return Usuario.query.filter_by(email=email).first()

def is_platform_admin(usuario_id):
    return UsuarioAdminPlataforma.query.filter_by(usuario_id=usuario_id).first() is not None

def tenant_memberships(usuario_id):
    rows = (
        db.session.query(UsuarioEmpresa.empresa_id, Empresa.nombre)
        .join(Empresa, Empresa.empresa_id == UsuarioEmpresa.empresa_id)
        .filter(UsuarioEmpresa.usuario_id == usuario_id)
        .filter(UsuarioEmpresa.activo.is_(True))
        .filter(Empresa.estado == "ACTIVA")
        .order_by(UsuarioEmpresa.empresa_id.asc())
        .all()
    )
    return [{"empresa_id": int(r[0]), "nombre": r[1]} for r in rows]

def get_tenant_user(empresa_id, usuario_id):
    return UsuarioEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first()

def get_roles_for_user(empresa_id, usuario_id):
    roles = []
    if UsuarioAdminEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
        roles.append("TENANT_ADMIN")
    if UsuarioVendedor.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
        roles.append("SELLER")
    if UsuarioEncargadoInventario.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
        roles.append("INVENTORY")
    return roles

def touch_usuario_login(usuario):
    usuario.ultimo_login = datetime.now(timezone.utc)
    db.session.commit()

def clients_by_email(email):
    rows = (
        db.session.query(Cliente.cliente_id, ClienteEmpresa.empresa_id, Empresa.nombre)
        .join(ClienteEmpresa, ClienteEmpresa.cliente_id == Cliente.cliente_id)
        .join(Empresa, Empresa.empresa_id == ClienteEmpresa.empresa_id)
        .filter(Cliente.email == email)
        .filter(Cliente.activo.is_(True))
        .filter(ClienteEmpresa.activo.is_(True))
        .filter(Empresa.estado == "ACTIVA")
        .order_by(ClienteEmpresa.empresa_id.asc())
        .all()
    )
    return [{"cliente_id": int(r[0]), "empresa_id": int(r[1]), "nombre": r[2]} for r in rows]

def get_cliente_by_email(email):
    return Cliente.query.filter_by(email=email).first()

def get_cliente_for_tenant(empresa_id, cliente_id):
    row = (
        db.session.query(Cliente)
        .join(ClienteEmpresa, ClienteEmpresa.cliente_id == Cliente.cliente_id)
        .filter(ClienteEmpresa.empresa_id == int(empresa_id))
        .filter(ClienteEmpresa.cliente_id == int(cliente_id))
        .filter(ClienteEmpresa.activo.is_(True))
        .first()
    )
    return row

def touch_cliente_login(cliente):
    cliente.ultimo_login = datetime.now(timezone.utc)
    db.session.commit()
