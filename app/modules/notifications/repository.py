from datetime import datetime, timezone

from app.extensions import db
from app.database.models.notificacion import Notificacion
from app.database.models.usuario import (
    Usuario,
    UsuarioEmpresa,
    UsuarioAdminEmpresa,
    UsuarioVendedor,
    UsuarioEncargadoInventario,
    UsuarioEncargadoInventario,
)

# -------------------------
# CREATE
# -------------------------


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


def create_for_client(empresa_id: int, cliente_id: int, canal: str, titulo: str, cuerpo: str) -> Notificacion:
    n = Notificacion(
        empresa_id=int(empresa_id),
        actor_type="client",
        usuario_id=None,
        cliente_id=int(cliente_id),
        canal=str(canal),
        titulo=str(titulo),
        cuerpo=str(cuerpo),
    )
    db.session.add(n)
    return n

# -------------------------
# RECIPIENTS
# -------------------------
def platform_admin_user_ids(active_only: bool = True) -> set[int]:
    q = (
        db.session.query(UsuarioAdminPlataforma.usuario_id)
        .join(Usuario, Usuario.usuario_id == UsuarioAdminPlataforma.usuario_id)
    )
    if active_only:
        q = q.filter(Usuario.activo.is_(True))

    return {int(r[0]) for r in q.all()}


def tenant_recipient_user_ids_by_roles(empresa_id: int, roles: set[str]) -> set[int]:
    roles = set(roles or set())
    ids: set[int] = set()

    if "TENANT_ADMIN" in roles:
        rows = (
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
        for r in rows:
            ids.add(int(r[0]))

    if "SELLER" in roles:
        rows = (
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
        for r in rows:
            ids.add(int(r[0]))

    if "INVENTORY" in roles:
        rows = (
            db.session.query(UsuarioEncargadoInventario.usuario_id)
            .join(
                UsuarioEmpresa,
                (UsuarioEmpresa.empresa_id == UsuarioEncargadoInventario.empresa_id)
                & (UsuarioEmpresa.usuario_id == UsuarioEncargadoInventario.usuario_id),
                )
            .filter(UsuarioEncargadoInventario.empresa_id == int(empresa_id))
            .filter(UsuarioEmpresa.activo.is_(True))
            .all()
        )
        for r in rows:
            ids.add(int(r[0]))

    return ids

# -------------------------
# TENANT USER LIST/COUNT/READ
# -------------------------
def list_notifications_user(
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


def unread_count_user(empresa_id: int, usuario_id: int, include_all: bool) -> int:
    q = (
        db.session.query(db.func.count(Notificacion.notificacion_id))
        .filter(Notificacion.empresa_id == int(empresa_id))
        .filter(Notificacion.actor_type == "user")
        .filter(Notificacion.leido_en.is_(None))
    )
    if not include_all:
        q = q.filter(Notificacion.usuario_id == int(usuario_id))
    return int(q.scalar() or 0)


def get_for_update_user(empresa_id: int, notificacion_id: int) -> Notificacion | None:
    return (
        db.session.query(Notificacion)
        .filter(Notificacion.empresa_id == int(empresa_id))
        .filter(Notificacion.notificacion_id == int(notificacion_id))
        .filter(Notificacion.actor_type == "user")
        .with_for_update()
        .first()
    )

# -------------------------
# CLIENT LIST/COUNT/READ
# -------------------------

def list_notifications_client(
        empresa_id: int,
        cliente_id: int,
        unread_only: bool,
        limit: int,
        offset: int,
):
    q = (
        db.session.query(Notificacion)
        .filter(Notificacion.empresa_id == int(empresa_id))
        .filter(Notificacion.actor_type == "client")
        .filter(Notificacion.cliente_id == int(cliente_id))
    )

    if unread_only:
        q = q.filter(Notificacion.leido_en.is_(None))

    q = q.order_by(Notificacion.creado_en.desc())

    if limit is not None:
        q = q.limit(int(limit))
    if offset is not None:
        q = q.offset(int(offset))

    return q.all()


def unread_count_client(empresa_id: int, cliente_id: int) -> int:
    q = (
        db.session.query(db.func.count(Notificacion.notificacion_id))
        .filter(Notificacion.empresa_id == int(empresa_id))
        .filter(Notificacion.actor_type == "client")
        .filter(Notificacion.cliente_id == int(cliente_id))
        .filter(Notificacion.leido_en.is_(None))
    )
    return int(q.scalar() or 0)


def get_for_update_client(empresa_id: int, notificacion_id: int, cliente_id: int) -> Notificacion | None:
    return (
        db.session.query(Notificacion)
        .filter(Notificacion.empresa_id == int(empresa_id))
        .filter(Notificacion.notificacion_id == int(notificacion_id))
        .filter(Notificacion.actor_type == "client")
        .filter(Notificacion.cliente_id == int(cliente_id))
        .with_for_update()
        .first()
    )

# -------------------------
# PLATFORM ADMIN LIST/COUNT/READ  (NUEVO)
# -------------------------

def list_notifications_platform_admin(usuario_id: int, unread_only: bool, limit: int, offset: int):
    q = (
        db.session.query(Notificacion)
        .filter(Notificacion.actor_type == "user")
        .filter(Notificacion.usuario_id == int(usuario_id))
    )

    if unread_only:
        q = q.filter(Notificacion.leido_en.is_(None))

    q = q.order_by(Notificacion.creado_en.desc())

    if limit is not None:
        q = q.limit(int(limit))
    if offset is not None:
        q = q.offset(int(offset))

    return q.all()


def unread_count_platform_admin(usuario_id: int) -> int:
    q = (
        db.session.query(db.func.count(Notificacion.notificacion_id))
        .filter(Notificacion.actor_type == "user")
        .filter(Notificacion.usuario_id == int(usuario_id))
        .filter(Notificacion.leido_en.is_(None))
    )
    return int(q.scalar() or 0)


def get_for_update_platform_admin(usuario_id: int, notificacion_id: int) -> Notificacion | None:
    return (
        db.session.query(Notificacion)
        .filter(Notificacion.actor_type == "user")
        .filter(Notificacion.usuario_id == int(usuario_id))
        .filter(Notificacion.notificacion_id == int(notificacion_id))
        .with_for_update()
        .first()
    )

# -------------------------
# COMMON
# -------------------------

def exists_same_notification_today(empresa_id: int, usuario_id: int, titulo: str, cuerpo: str) -> bool:
    """
    Anti-spam simple: si ya existe HOY la misma notificación (titulo+cuerpo) para ese usuario, no repetimos.
    """
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    return (
        db.session.query(Notificacion.notificacion_id)
        .filter(Notificacion.empresa_id == int(empresa_id))
        .filter(Notificacion.actor_type == "user")
        .filter(Notificacion.usuario_id == int(usuario_id))
        .filter(Notificacion.titulo == str(titulo))
        .filter(Notificacion.cuerpo == str(cuerpo))
        .filter(Notificacion.creado_en >= start)
        .first()
        is not None
    )

def mark_as_read(n: Notificacion) -> Notificacion:
    if n.leido_en is None:
        n.leido_en = datetime.now(timezone.utc)
        db.session.add(n)
    return n
