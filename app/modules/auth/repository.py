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


def get_usuario_by_email(email: str):
    if not email:
        return None
    return Usuario.query.filter_by(email=email).first()


def is_platform_admin(usuario_id: int) -> bool:
    if not usuario_id:
        return False
    return UsuarioAdminPlataforma.query.filter_by(usuario_id=usuario_id).first() is not None


def tenant_memberships(usuario_id: int):
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


def get_tenant_user(empresa_id: int, usuario_id: int):
    return UsuarioEmpresa.query.filter_by(
        empresa_id=empresa_id,
        usuario_id=usuario_id,
    ).first()


def get_roles_for_user(empresa_id: int, usuario_id: int):
    roles = []
    if UsuarioAdminEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
        roles.append("TENANT_ADMIN")
    if UsuarioVendedor.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
        roles.append("SELLER")
    if UsuarioEncargadoInventario.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
        roles.append("INVENTORY")
    return roles


def clients_by_email(email: str):
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


def get_cliente_by_email(email: str):
    if not email:
        return None
    return Cliente.query.filter_by(email=email).first()


def get_cliente_for_tenant(empresa_id: int, cliente_id: int):
    return (
        db.session.query(Cliente)
        .join(ClienteEmpresa, ClienteEmpresa.cliente_id == Cliente.cliente_id)
        .filter(ClienteEmpresa.empresa_id == empresa_id)
        .filter(ClienteEmpresa.cliente_id == cliente_id)
        .filter(ClienteEmpresa.activo.is_(True))
        .first()
    )


def empresa_activa_exists(empresa_id: int) -> bool:
    if not empresa_id:
        return False
    return (
            db.session.query(Empresa.empresa_id)
            .filter(Empresa.empresa_id == int(empresa_id))
            .filter(Empresa.estado == "ACTIVA")
            .first()
            is not None
    )


def cliente_link_exists(empresa_id: int, cliente_id: int) -> bool:
    if not empresa_id or not cliente_id:
        return False
    return (
            db.session.query(ClienteEmpresa.cliente_id)
            .filter(ClienteEmpresa.empresa_id == int(empresa_id))
            .filter(ClienteEmpresa.cliente_id == int(cliente_id))
            .filter(ClienteEmpresa.activo.is_(True))
            .first()
            is not None
    )


def create_cliente(email: str, password_hash: str, nombre_razon: str = None, telefono: str = None):
    c = Cliente(
        email=email,
        password_hash=password_hash,
        nombre_razon=nombre_razon,
        telefono=telefono,
        activo=True,
    )
    db.session.add(c)
    db.session.flush()
    return c


def create_cliente_link(empresa_id: int, cliente_id: int):
    link = ClienteEmpresa(
        empresa_id=int(empresa_id),
        cliente_id=int(cliente_id),
        activo=True,
    )
    db.session.add(link)
    db.session.flush()
    return link
