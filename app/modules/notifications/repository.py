from datetime import datetime, timezone

from app.extensions import db
from app.database.models.notificacion import Notificacion
from app.database.models.usuario import (
    UsuarioEmpresa,
    UsuarioAdminEmpresa,
    UsuarioVendedor,
)

def create_for_user(empresa_id: int, usuario_id: int, canal: str, titulo: str, cuerpo: str) -> Notificacion:
    n = Notificacion(
        empresa_id=int(empresa_id),
        actor_type="user",
        usuario_id=int(usuario_id),
        cliente_id=None,
        canal=str(canal),
        titulo=str(titulo),
        cuerpo=str(cuerpo),
    )
    db.session.add(n)
    return n


def list_notifications(
    empresa_id: int,
    usuario_id: int,
    include_all: bool,
    unread_only: bool,
    limit: int,
    offset: int,
):
    q = (
        db.session.query(Notificacion)
        .filter(Notificacion.empresa_id == int(empresa_id))
        .filter(Notificacion.actor_type == "user")
    )

    if not include_all:
        q = q.filter(Notificacion.usuario_id == int(usuario_id))

    if unread_only:
        q = q.filter(Notificacion.leido_en.is_(None))

    q = q.order_by(Notificacion.creado_en.desc())

    if limit is not None:
        q = q.limit(int(limit))
    if offset is not None:
        q = q.offset(int(offset))

    return q.all()


def unread_count(empresa_id: int, usuario_id: int, include_all: bool) -> int:
    q = (
        db.session.query(db.func.count(Notificacion.notificacion_id))
        .filter(Notificacion.empresa_id == int(empresa_id))
        .filter(Notificacion.actor_type == "user")
        .filter(Notificacion.leido_en.is_(None))
    )
    if not include_all:
        q = q.filter(Notificacion.usuario_id == int(usuario_id))
    return int(q.scalar() or 0)


def get_for_update(empresa_id: int, notificacion_id: int) -> Notificacion | None:
    return (
        db.session.query(Notificacion)
        .filter(Notificacion.empresa_id == int(empresa_id))
        .filter(Notificacion.notificacion_id == int(notificacion_id))
        .with_for_update()
        .first()
    )


def mark_as_read(n: Notificacion) -> Notificacion:
    if n.leido_en is None:
        n.leido_en = datetime.now(timezone.utc)
        db.session.add(n)
    return n


def stock_alert_recipient_user_ids(empresa_id: int) -> set[int]:
    """
    Admin tenant + vendedores activos del tenant (empresa).
    """
    ids: set[int] = set()

    # Admins activos
    rows_a = (
        db.session.query(UsuarioAdminEmpresa.usuario_id)
        .join(
            UsuarioEmpresa,
            (UsuarioEmpresa.empresa_id == UsuarioAdminEmpresa.empresa_id)
            & (UsuarioEmpresa.usuario_id == UsuarioAdminEmpresa.usuario_id),
        )
        .filter(UsuarioAdminEmpresa.empresa_id == int(empresa_id))
        .filter(UsuarioEmpresa.activo.is_(True))
        .all()
    )

    # Vendedores activos
    rows_v = (
        db.session.query(UsuarioVendedor.usuario_id)
        .join(
            UsuarioEmpresa,
            (UsuarioEmpresa.empresa_id == UsuarioVendedor.empresa_id)
            & (UsuarioEmpresa.usuario_id == UsuarioVendedor.usuario_id),
        )
        .filter(UsuarioVendedor.empresa_id == int(empresa_id))
        .filter(UsuarioEmpresa.activo.is_(True))
        .all()
    )

    for r in rows_a:
        ids.add(int(r[0]))
    for r in rows_v:
        ids.add(int(r[0]))

    return ids
