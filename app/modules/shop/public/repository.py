from sqlalchemy import func
from app.extensions import db
from app.database.models.empresa import Empresa
from app.database.models.empresa_settings import EmpresaSettings
from app.database.models.producto import Producto


def list_public_empresas(q=None, page=1, page_size=12):
    query = (
        db.session.query(Empresa, EmpresaSettings)
        .outerjoin(EmpresaSettings, EmpresaSettings.empresa_id == Empresa.empresa_id)
        .filter(Empresa.estado == "ACTIVA")
    )

    if q:
        qq = f"%{q}%"
        query = query.filter((Empresa.nombre.ilike(qq)) | (Empresa.nit.ilike(qq)))

    total = query.count()
    rows = (
        query.order_by(Empresa.empresa_id.asc())
        .offset((int(page) - 1) * int(page_size))
        .limit(int(page_size))
        .all()
    )
    return rows, total


def get_public_empresa(empresa_id: int):
    return (
        db.session.query(Empresa, EmpresaSettings)
        .outerjoin(EmpresaSettings, EmpresaSettings.empresa_id == Empresa.empresa_id)
        .filter(Empresa.empresa_id == int(empresa_id))
        .filter(Empresa.estado == "ACTIVA")
        .first()
    )


def list_random_products(limit=12):
    rows = (
        db.session.query(Producto, Empresa, EmpresaSettings)
        .join(Empresa, Empresa.empresa_id == Producto.empresa_id)
        .outerjoin(EmpresaSettings, EmpresaSettings.empresa_id == Empresa.empresa_id)
        .filter(Empresa.estado == "ACTIVA")
        .filter(Producto.activo.is_(True))
        .filter(Producto.stock > 0)
        .order_by(func.random())
        .limit(int(limit))
        .all()
    )
    return rows


def list_random_products_by_empresa(empresa_id: int, limit=12):
    rows = (
        db.session.query(Producto, Empresa, EmpresaSettings)
        .join(Empresa, Empresa.empresa_id == Producto.empresa_id)
        .outerjoin(EmpresaSettings, EmpresaSettings.empresa_id == Empresa.empresa_id)
        .filter(Empresa.estado == "ACTIVA")
        .filter(Producto.empresa_id == int(empresa_id))
        .filter(Producto.activo.is_(True))
        .filter(Producto.stock > 0)
        .order_by(func.random())
        .limit(int(limit))
        .all()
    )
    return rows
