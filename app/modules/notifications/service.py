from decimal import Decimal

from app.modules.notifications import repository as repo


def _dec(v) -> Decimal:
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


class NotificationsService:
    @staticmethod
    def list_notifications_user(empresa_id: int, usuario_id: int, include_all: bool, unread_only: bool, limit: int, offset: int):
        rows = repo.list_notifications_user(
            empresa_id=int(empresa_id),
            usuario_id=int(usuario_id),
            include_all=bool(include_all),
            unread_only=bool(unread_only),
            limit=int(limit),
            offset=int(offset),
        )
        return [n.to_dict() for n in rows]

    @staticmethod
    def unread_count_user(empresa_id: int, usuario_id: int, include_all: bool) -> int:
        return repo.unread_count_user(int(empresa_id), int(usuario_id), include_all=bool(include_all))

    @staticmethod
    def mark_as_read_user(empresa_id: int, usuario_id: int, include_all: bool, notificacion_id: int):
        n = repo.get_for_update_user(int(empresa_id), int(notificacion_id))
        if not n:
            return None, "not_found"
        if not include_all and int(n.usuario_id or 0) != int(usuario_id):
            return None, "forbidden"
        repo.mark_as_read(n)
        return n.to_dict(), None

    @staticmethod
    def list_notifications_client(empresa_id: int, cliente_id: int, unread_only: bool, limit: int, offset: int):
        rows = repo.list_notifications_client(
            empresa_id=int(empresa_id),
            cliente_id=int(cliente_id),
            unread_only=bool(unread_only),
            limit=int(limit),
            offset=int(offset),
        )
        return [n.to_dict() for n in rows]

    @staticmethod
    def unread_count_client(empresa_id: int, cliente_id: int) -> int:
        return repo.unread_count_client(int(empresa_id), int(cliente_id))

    @staticmethod
    def mark_as_read_client(empresa_id: int, cliente_id: int, notificacion_id: int):
        n = repo.get_for_update_client(int(empresa_id), int(notificacion_id), int(cliente_id))
        if not n:
            return None, "not_found"
        repo.mark_as_read(n)
        return n.to_dict(), None

    @staticmethod
    def should_fire_stock_zero(prev_stock, new_stock) -> bool:
        prev = _dec(prev_stock)
        new = _dec(new_stock)
        return prev > 0 and new <= 0

    @staticmethod
    def should_fire_stock_min(prev_stock, stock_min, new_stock) -> bool:
        ps = _dec(prev_stock)
        nm = _dec(stock_min)
        ns = _dec(new_stock)
        if ns <= 0:
            return False
        return ps > nm and ns <= nm

    @staticmethod
    def notify_tenant_roles(empresa_id: int, roles: set[str], titulo: str, cuerpo: str, canal: str = "IN_APP"):
        ids = repo.tenant_recipient_user_ids_by_roles(int(empresa_id), set(roles or set()))
        for uid in ids:
            repo.create_for_user(int(empresa_id), int(uid), str(canal), str(titulo), str(cuerpo))

    @staticmethod
    def notify_client(empresa_id: int, cliente_id: int, titulo: str, cuerpo: str, canal: str = "IN_APP"):
        repo.create_for_client(int(empresa_id), int(cliente_id), str(canal), str(titulo), str(cuerpo))

    @staticmethod
    def notify_stock_zero(empresa_id: int, producto_id: int, codigo: str | None, descripcion: str | None):
        code = (codigo or "").strip()
        desc = (descripcion or "").strip()
        titulo = "Stock agotado"
        if code:
            titulo = f"Stock agotado: {code}"
        cuerpo = f"producto_id={int(producto_id)}"
        if desc:
            cuerpo += f" descripcion={desc}"
        NotificationsService.notify_tenant_roles(int(empresa_id), {"TENANT_ADMIN", "INVENTORY", "SELLER"}, titulo, cuerpo)

    @staticmethod
    def notify_stock_min(empresa_id: int, producto_id: int, codigo: str | None, descripcion: str | None, stock, stock_min):
        code = (codigo or "").strip()
        desc = (descripcion or "").strip()
        titulo = "Stock bajo"
        if code:
            titulo = f"Stock bajo: {code}"
        cuerpo = f"producto_id={int(producto_id)} stock={_dec(stock)} stock_min={int(_dec(stock_min))}"
        if desc:
            cuerpo += f" descripcion={desc}"
        NotificationsService.notify_tenant_roles(int(empresa_id), {"TENANT_ADMIN", "INVENTORY"}, titulo, cuerpo)

    @staticmethod
    def notify_order_created(empresa_id: int, venta_id: int, cliente_id: int, total):
        titulo = "Nuevo pedido"
        cuerpo = f"venta_id={int(venta_id)} cliente_id={int(cliente_id)} total={_dec(total)}"
        NotificationsService.notify_tenant_roles(int(empresa_id), {"TENANT_ADMIN", "SELLER"}, titulo, cuerpo)
        NotificationsService.notify_client(int(empresa_id), int(cliente_id), "Pedido creado", f"venta_id={int(venta_id)} total={_dec(total)}")

    @staticmethod
    def notify_order_status_changed(empresa_id: int, venta_id: int, cliente_id: int, old_status: str | None, new_status: str | None):
        old_s = str(old_status or "").strip()
        new_s = str(new_status or "").strip()
        cuerpo = f"venta_id={int(venta_id)} estado={old_s}->{new_s}"
        NotificationsService.notify_tenant_roles(int(empresa_id), {"TENANT_ADMIN", "SELLER"}, "Pedido actualizado", cuerpo)
        NotificationsService.notify_client(int(empresa_id), int(cliente_id), "Estado de pedido", cuerpo)
