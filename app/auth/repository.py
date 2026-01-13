from datetime import datetime, timezone

from app.db.models.cliente import Cliente
from app.db.models.usuario import (
    Usuario,
    UsuarioAdminPlataforma,
    UsuarioEmpresa,
    UsuarioAdminEmpresa,
    UsuarioVendedor,
    UsuarioEncargadoInventario,
)
from app.extensions import db


def get_usuario_by_email(email):
    return Usuario.query.filter_by(email=email).first()


def is_platform_admin(usuario_id):
    return UsuarioAdminPlataforma.query.filter_by(usuario_id=usuario_id).first() is not None


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


def get_cliente(empresa_id, email):
    return Cliente.query.filter_by(empresa_id=empresa_id, email=email).first()


def touch_cliente_login(cliente):
    cliente.ultimo_login = datetime.now(timezone.utc)
    db.session.commit()
