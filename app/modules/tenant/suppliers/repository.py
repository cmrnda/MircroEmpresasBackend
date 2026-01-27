from app.extensions import db
from app.database.models.producto import Producto
from app.database.models.proveedor import Proveedor
from app.database.models.proveedor_producto import ProveedorProducto

def list_suppliers(empresa_id: int, q=None, include_inactivos=False):
    query = db.session.query(Proveedor).filter(Proveedor.empresa_id == int(empresa_id))
    if not include_inactivos:
        query = query.filter(Proveedor.activo.is_(True))
    if q:
        qq = f"%{q}%"
        query = query.filter(Proveedor.nombre.ilike(qq) | Proveedor.nit.ilike(qq))
    return query.order_by(Proveedor.proveedor_id.asc()).all()

def get_supplier(empresa_id: int, proveedor_id: int, include_inactivos=False):
    q = (
        db.session.query(Proveedor)
        .filter(Proveedor.empresa_id == int(empresa_id))
        .filter(Proveedor.proveedor_id == int(proveedor_id))
    )
    if not include_inactivos:
        q = q.filter(Proveedor.activo.is_(True))
    return q.first()

def get_supplier_any(empresa_id: int, proveedor_id: int):
    return (
        db.session.query(Proveedor)
        .filter(Proveedor.empresa_id == int(empresa_id))
        .filter(Proveedor.proveedor_id == int(proveedor_id))
        .first()
    )

def create_supplier(empresa_id: int, payload: dict):
    s = Proveedor(
        empresa_id=int(empresa_id),
        nombre=str(payload.get("nombre")).strip(),
        nit=(payload.get("nit") or "").strip() or None,
        telefono=(payload.get("telefono") or "").strip() or None,
        direccion=(payload.get("direccion") or "").strip() or None,
        email=(payload.get("email") or "").strip() or None,
        activo=True,
    )
    db.session.add(s)
    db.session.flush()
    return s

def update_supplier(s: Proveedor, payload: dict):
    if "nombre" in payload and payload.get("nombre") is not None:
        s.nombre = str(payload.get("nombre")).strip()
    if "nit" in payload:
        s.nit = (payload.get("nit") or "").strip() or None
    if "telefono" in payload:
        s.telefono = (payload.get("telefono") or "").strip() or None
    if "direccion" in payload:
        s.direccion = (payload.get("direccion") or "").strip() or None
    if "email" in payload:
        s.email = (payload.get("email") or "").strip() or None
    if "activo" in payload and payload.get("activo") is not None:
        s.activo = bool(payload.get("activo"))
    db.session.add(s)
    return s

def soft_delete_supplier(s: Proveedor):
    s.activo = False
    db.session.add(s)
    return s

def restore_supplier(s: Proveedor):
    s.activo = True
    db.session.add(s)
    return s


def list_products_with_suppliers(
    empresa_id: int,
    proveedor_id: int | None,
    q: str | None,
    limit: int,
    offset: int,
):
    qry = (
        db.session.query(Producto, Proveedor)
        .join(
            ProveedorProducto,
            (ProveedorProducto.empresa_id == Producto.empresa_id)
            & (ProveedorProducto.producto_id == Producto.producto_id),
        )
        .join(
            Proveedor,
            (Proveedor.empresa_id == ProveedorProducto.empresa_id)
            & (Proveedor.proveedor_id == ProveedorProducto.proveedor_id),
        )
        .filter(Producto.empresa_id == int(empresa_id))
    )

    if proveedor_id:
        qry = qry.filter(Proveedor.proveedor_id == int(proveedor_id))

    if q:
        qq = f"%{str(q).strip()}%"
        qry = qry.filter(
            (Producto.codigo.ilike(qq))
            | (Producto.descripcion.ilike(qq))
            | (Proveedor.nombre.ilike(qq))
        )

    qry = (
        qry.order_by(Producto.producto_id.asc(), Proveedor.proveedor_id.asc())
        .limit(int(limit))
        .offset(int(offset))
    )

    return qry.all()

def link_product_to_supplier(empresa_id: int, proveedor_id: int, producto_id: int) -> bool:
    """
    Inserta vínculo (empresa_id, proveedor_id, producto_id).
    Retorna True si se creó, False si ya existía.
    """
    empresa_id = int(empresa_id)
    proveedor_id = int(proveedor_id)
    producto_id = int(producto_id)

    exists = (
        db.session.query(ProveedorProducto)
        .filter(ProveedorProducto.empresa_id == empresa_id)
        .filter(ProveedorProducto.proveedor_id == proveedor_id)
        .filter(ProveedorProducto.producto_id == producto_id)
        .first()
    )
    if exists:
        return False

    row = ProveedorProducto(
        empresa_id=empresa_id,
        proveedor_id=proveedor_id,
        producto_id=producto_id,
    )
    db.session.add(row)
    db.session.commit()
    return True


def unlink_product_from_supplier(empresa_id: int, proveedor_id: int, producto_id: int) -> bool:
    """
    Borra vínculo. Retorna True si borró algo, False si no existía.
    """
    empresa_id = int(empresa_id)
    proveedor_id = int(proveedor_id)
    producto_id = int(producto_id)

    q = (
        db.session.query(ProveedorProducto)
        .filter(ProveedorProducto.empresa_id == empresa_id)
        .filter(ProveedorProducto.proveedor_id == proveedor_id)
        .filter(ProveedorProducto.producto_id == producto_id)
    )

    row = q.first()
    if not row:
        return False

    db.session.delete(row)
    db.session.commit()
    return True