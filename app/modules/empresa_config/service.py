from app.modules.empresa_config.repository import EmpresaConfigRepository

_repo = EmpresaConfigRepository()

class EmpresaConfigService:
    def get_config(self, empresa_id: int) -> dict:
        cfg = _repo.create_default_if_missing(empresa_id)
        return cfg.to_dict() if hasattr(cfg, "to_dict") else {
            "empresa_id": cfg.empresa_id,
            "moneda": cfg.moneda,
            "tasa_impuesto": float(cfg.tasa_impuesto) if cfg.tasa_impuesto is not None else 0,
            "logo_url": cfg.logo_url,
            "actualizado_en": cfg.actualizado_en.isoformat() if cfg.actualizado_en else None,
        }

    def update_config(self, empresa_id: int, data: dict) -> dict:
        # Validaciones simples (ajustables a tu estándar)
        if "moneda" in data and data["moneda"] is not None:
            moneda = str(data["moneda"]).strip()
            if len(moneda) < 2 or len(moneda) > 10:
                raise ValueError("MONEDA_INVALID")

        if "tasa_impuesto" in data and data["tasa_impuesto"] is not None:
            try:
                tasa = float(data["tasa_impuesto"])
            except Exception:
                raise ValueError("TASA_INVALID")
            if tasa < 0 or tasa > 100:
                raise ValueError("TASA_OUT_OF_RANGE")

        cfg = _repo.update(empresa_id, data)
        return cfg.to_dict() if hasattr(cfg, "to_dict") else {
            "empresa_id": cfg.empresa_id,
            "moneda": cfg.moneda,
            "tasa_impuesto": float(cfg.tasa_impuesto) if cfg.tasa_impuesto is not None else 0,
            "logo_url": cfg.logo_url,
            "actualizado_en": cfg.actualizado_en.isoformat() if cfg.actualizado_en else None,
        }
