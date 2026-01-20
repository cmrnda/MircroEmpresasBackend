from decimal import Decimal
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.modules.inventory.repository import (
    list_inventory,
    get_existencia_for_update,
    create_movimiento,
)

def _usuario_id_from_jwt():
    ident = get_jwt_identity()
    if isinstance(ident, dict):
        for k in ("usuario_id", "id", "sub"):
            if ident.get(k) is not None:
                return int(ident.get(k))
        return None
    try:
        return int(ident)
    except Exception:
        return None

def _inv_item_dict(p, qty):
    return {
        "producto_id": int(p.producto_id),
        "codigo": p.codigo,
        "descripcion": p.descripcion,
        "activo": bool(p.activo),
        "stock_min": int(p.stock_min),
        "cantidad_actual": float(qty) if qty is not None else 0.0,
    }

def tenant_inventory_list(empresa_id: int, q=None, page=1, page_size=20, include_inactivos=False):
    rows, total, page, page_size = list_inventory(empresa_id, q, page, page_size, include_inactivos)
    return {
        "items": [_inv_item_dict(p, qty) for (p, qty) in rows],
        "page": int(page),
        "page_size": int(page_size),
        "total": int(total),
    }

def tenant_inventory_adjust(empresa_id: int, payload: dict):
    usuario_id = _usuario_id_from_jwt()
    if not usuario_id:
        return None, "unauthorized"

    try:
        producto_id = int(payload.get("producto_id"))
        delta = Decimal(str(payload.get("delta")))
    except Exception:
        return None, "invalid_payload"

    if delta == 0:
        return None, "invalid_payload"

    tipo = (payload.get("tipo") or "").strip() or ("AJUSTE_ENTRADA" if delta > 0 else "AJUSTE_SALIDA")
    ref_tabla = (payload.get("ref_tabla") or "").strip() or None
    ref_id = payload.get("ref_id")
    ref_id = int(ref_id) if ref_id is not None else None

    with db.session.begin():
        ex = get_existencia_for_update(empresa_id, producto_id)
        nueva = Decimal(str(ex.cantidad_actual)) + delta
        if nueva < 0:
            return None, "stock_insuficiente"
        ex.cantidad_actual = nueva
        create_movimiento(empresa_id, producto_id, tipo, abs(delta), ref_tabla, ref_id, usuario_id)

    return {"ok": True, "producto_id": producto_id, "cantidad_actual": float(nueva)}, None
