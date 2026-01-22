from decimal import Decimal

from app.modules.notifications import repository as repo


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


class NotificationsService:
    @staticmethod
    def list_notifications(
        empresa_id: int,
        usuario_id: int,
        include_all: bool,
        unread_only: bool,
        limit: int,
        offset: int,
    ):
        rows = repo.list_notifications(
            empresa_id=int(empresa_id),
            usuario_id=int(usuario_id),
            include_all=bool(include_all),
            unread_only=bool(unread_only),
            limit=int(limit),
            offset=int(offset),
        )
        return [n.to_dict() for n in rows]

    @staticmethod
    def unread_count(empresa_id: int, usuario_id: int, include_all: bool) -> int:
        return repo.unread_count(int(empresa_id), int(usuario_id), include_all=bool(include_all))

    @staticmethod
    def mark_as_read(empresa_id: int, usuario_id: int, include_all: bool, notificacion_id: int):
        n = repo.get_for_update(int(empresa_id), int(notificacion_id))
        if not n:
            return None, "not_found"

        # si no es admin (include_all=False), solo puede marcar las suyas
        if not include_all and int(n.usuario_id or 0) != int(usuario_id):
            return None, "forbidden"

        repo.mark_as_read(n)
        return n.to_dict(), None

    @staticmethod
    def notify_stock_zero(empresa_id: int, producto_id: int, codigo: str | None, descripcion: str | None):
        """
        Crea notificación IN_APP para Admin tenant + Vendedores cuando un producto llega a 0 stock.
        """
        recipients = repo.stock_alert_recipient_user_ids(int(empresa_id))
        if not recipients:
            return

        code = (codigo or "").strip()
        desc = (descripcion or "").strip()

        titulo = "Stock agotado"
        if code:
            titulo = f"Stock agotado: {code}"

        cuerpo = f"El producto {int(producto_id)}"
        if desc:
            cuerpo += f" ({desc})"
        cuerpo += " llegó a 0 en stock."

        for uid in recipients:
            repo.create_for_user(int(empresa_id), int(uid), "IN_APP", titulo, cuerpo)

    @staticmethod
    def should_fire_stock_zero(prev_stock, new_stock) -> bool:
        """
        Dispara solo si hubo transición: >0  ->  <=0
        (evita spam si ya estaba en 0)
        """
        prev = _dec(prev_stock)
        new = _dec(new_stock)
        return prev > 0 and new <= 0
