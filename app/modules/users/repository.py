from werkzeug.security import generate_password_hash

from app.db.models.usuario import (
    Usuario,
    UsuarioEmpresa,
    UsuarioAdminEmpresa,
    UsuarioVendedor,
    UsuarioEncargadoInventario,
)
from app.extensions import db


def list_users(empresa_id):
    rows = (
        db.session.query(Usuario, UsuarioEmpresa)
        .join(UsuarioEmpresa, UsuarioEmpresa.usuario_id == Usuario.usuario_id)
        .filter(UsuarioEmpresa.empresa_id == empresa_id)
        .all()
    )
    return rows


def get_user(empresa_id, usuario_id):
    ue = UsuarioEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first()
    if not ue:
        return None, None
    u = Usuario.query.filter_by(usuario_id=usuario_id).first()
    return u, ue


def create_user_global(email, password):
    u = Usuario(email=email, password_hash=generate_password_hash(password))
    db.session.add(u)
    db.session.flush()
    return u


def attach_user_to_tenant(empresa_id, usuario_id):
    ue = UsuarioEmpresa(empresa_id=empresa_id, usuario_id=usuario_id)
    db.session.add(ue)
    return ue


def set_roles(empresa_id, usuario_id, roles):
    UsuarioAdminEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
    UsuarioVendedor.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
    UsuarioEncargadoInventario.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()

    roles = set(roles or [])
    if "TENANT_ADMIN" in roles:
        db.session.add(UsuarioAdminEmpresa(empresa_id=empresa_id, usuario_id=usuario_id))
    if "SELLER" in roles:
        db.session.add(UsuarioVendedor(empresa_id=empresa_id, usuario_id=usuario_id))
    if "INVENTORY" in roles:
        db.session.add(UsuarioEncargadoInventario(empresa_id=empresa_id, usuario_id=usuario_id))


def user_roles(empresa_id, usuario_id):
    roles = []
    if UsuarioAdminEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
        roles.append("TENANT_ADMIN")
    if UsuarioVendedor.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
        roles.append("SELLER")
    if UsuarioEncargadoInventario.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
        roles.append("INVENTORY")
    return roles


def update_user(u, ue, payload):
    if payload.get("activo") is not None:
        u.activo = bool(payload.get("activo"))
    if payload.get("tenant_activo") is not None:
        ue.activo = bool(payload.get("tenant_activo"))
    if payload.get("password"):
        u.password_hash = generate_password_hash(payload.get("password"))
    db.session.commit()


def detach_user(empresa_id, usuario_id):
    UsuarioAdminEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
    UsuarioVendedor.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
    UsuarioEncargadoInventario.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
    UsuarioEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
    db.session.commit()
