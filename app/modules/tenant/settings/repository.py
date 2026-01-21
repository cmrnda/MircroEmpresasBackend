from app.extensions import db
from app.database.models.empresa_settings import EmpresaSettings

def get_settings(empresa_id: int):
    return db.session.query(EmpresaSettings).filter_by(empresa_id=int(empresa_id)).first()

def ensure_settings(empresa_id: int):
    s = get_settings(int(empresa_id))
    if s:
        return s
    s = EmpresaSettings(empresa_id=int(empresa_id))
    db.session.add(s)
    db.session.flush()
    return s

def update_settings(s: EmpresaSettings, payload: dict):
    allowed = {"moneda", "tasa_impuesto", "logo_url"}
    for k in allowed:
        if k in payload:
            setattr(s, k, payload.get(k))
    db.session.add(s)
    return s
