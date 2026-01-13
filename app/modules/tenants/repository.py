from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.db.models.empresa import Empresa
from app.db.models.usuario import Usuario, UsuarioEmpresa, UsuarioAdminEmpresa
from app.extensions import db


def list_empresas():
    return Empresa.query.order_by(Empresa.empresa_id.desc()).all()


def get_empresa(empresa_id):
    return Empresa.query.filter_by(empresa_id=empresa_id).first()


def create_empresa(nombre, nit):
    e = Empresa(nombre=nombre, nit=nit)
    db.session.add(e)
    db.session.flush()
    return e


def update_empresa(e, nombre, nit, estado):
    if nombre is not None:
        e.nombre = nombre
    if nit is not None:
        e.nit = nit
    if estado is not None:
        e.estado = estado
    db.session.commit()
    return e


def delete_empresa(e):
    db.session.delete(e)
    db.session.commit()


def create_tenant_admin_user(empresa_id, email, password):
    try:
        u = Usuario(email=email, password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.flush()

        ue = UsuarioEmpresa(empresa_id=empresa_id, usuario_id=u.usuario_id)
        db.session.add(ue)
        db.session.flush()

        role = UsuarioAdminEmpresa(empresa_id=empresa_id, usuario_id=u.usuario_id)
        db.session.add(role)

        db.session.commit()
        return u
    except IntegrityError:
        db.session.rollback()
        raise
