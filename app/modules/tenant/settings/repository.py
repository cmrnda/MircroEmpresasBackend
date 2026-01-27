from app.extensions import db
from app.database.models.empresa import Empresa
from app.database.models.empresa_settings import EmpresaSettings


class EmpresaSettingsRepository:
    def get_empresa(self, empresa_id: int) -> Empresa | None:
        return db.session.get(Empresa, empresa_id)

    def get_settings(self, empresa_id: int) -> EmpresaSettings | None:
        return db.session.get(EmpresaSettings, empresa_id)

    def create_default_settings(self, empresa_id: int) -> EmpresaSettings:
        s = EmpresaSettings(empresa_id=empresa_id)
        db.session.add(s)
        db.session.flush()
        return s

    def save(self) -> None:
        db.session.commit()
