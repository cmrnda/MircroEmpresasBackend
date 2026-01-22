from app.extensions import db
from app.database.models.empresa import Empresa
from app.database.models.usuario import Usuario, UsuarioEmpresa, UsuarioAdminEmpresa
from app.security.password import hash_password

def list_empresas(q=None, include_inactivos=False):
    query = db.session.query(Empresa)
    if not include_inactivos:
        query = query.filter(Empresa.estado == "ACTIVA")
    if q:
        query = query.filter(Empresa.nombre.ilike(f"%{q}%"))
    return query.order_by(Empresa.empresa_id.asc()).all()

def get_empresa(empresa_id: int):
    return db.session.query(Empresa).filter(Empresa.empresa_id == int(empresa_id)).first()

def create_empresa(nombre: str, nit: str | None):
    e = Empresa(nombre=nombre, nit=nit)
    db.session.add(e)
    db.session.flush()
    return e

def update_empresa(e: Empresa, nombre=None, nit=None, estado=None):
    if nombre is not None:
        e.nombre = nombre
    if nit is not None:
        e.nit = nit
    if estado is not None:
        e.estado = estado
    db.session.add(e)
    return e

def soft_delete_empresa(e: Empresa):
    e.estado = "INACTIVA"
    db.session.add(e)
    return e

def create_tenant_admin_user(empresa_id: int, email: str, password: str):
    u = Usuario(email=email, password_hash=hash_password(password), activo=True)
    db.session.add(u)
    db.session.flush()

    ue = UsuarioEmpresa(empresa_id=int(empresa_id), usuario_id=int(u.usuario_id), activo=True)
    db.session.add(ue)

    role = UsuarioAdminEmpresa(empresa_id=int(empresa_id), usuario_id=int(u.usuario_id))
    db.session.add(role)

    return u
