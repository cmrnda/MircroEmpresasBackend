from app.extensions import db
from app.modules.platform.subscriptions.repository import ensure_settings, set_subscription_fields, list_tenants_with_settings

def platform_list_subscriptions(include_inactivos=False):
    rows = list_tenants_with_settings(include_inactivos=include_inactivos)
    out = []
    for e, s in rows:
        out.append({
            "empresa": e.to_dict(),
            "settings": s.to_dict() if s else None,
        })
    return out

def platform_get_subscription(empresa_id: int):
    s = ensure_settings(int(empresa_id))
    db.session.commit()
    return s.to_dict()

def platform_update_subscription(empresa_id: int, payload: dict):
    with db.session.begin():
        s = ensure_settings(int(empresa_id))
        set_subscription_fields(s, payload)
    return s.to_dict()
