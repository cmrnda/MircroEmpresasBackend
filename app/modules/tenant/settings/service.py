from app.extensions import db
from app.modules.tenant.settings.repository import ensure_settings, update_settings

def tenant_get_settings(empresa_id: int):
    s = ensure_settings(int(empresa_id))
    db.session.commit()
    return s.to_dict()

def tenant_update_settings(empresa_id: int, payload: dict):
    s = ensure_settings(int(empresa_id))
    update_settings(s, payload)
    db.session.commit()
    return s.to_dict()
