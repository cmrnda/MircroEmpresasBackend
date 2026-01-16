from app.extensions import db
from app.db.models.empresa_config import EmpresaConfig

class EmpresaConfigRepository:
    def get(self, empresa_id: int) -> EmpresaConfig | None:
        return EmpresaConfig.query.filter_by(empresa_id=empresa_id).first()

    def create_default_if_missing(self, empresa_id: int) -> EmpresaConfig:
        cfg = self.get(empresa_id)
        if cfg:
            return cfg

        cfg = EmpresaConfig(empresa_id=empresa_id)
        db.session.add(cfg)
        db.session.commit()
        return cfg

    def update(self, empresa_id: int, data: dict) -> EmpresaConfig:
        cfg = self.create_default_if_missing(empresa_id)

        if "moneda" in data and data["moneda"] is not None:
            cfg.moneda = str(data["moneda"]).strip()

        if "tasa_impuesto" in data and data["tasa_impuesto"] is not None:
            cfg.tasa_impuesto = data["tasa_impuesto"]

        if "logo_url" in data:  # permite setear null para borrar
            cfg.logo_url = data["logo_url"]

        # IMPORTANT: server_default no “actualiza solo” en updates.
        cfg.actualizado_en = db.func.now()

        db.session.commit()
        return cfg
