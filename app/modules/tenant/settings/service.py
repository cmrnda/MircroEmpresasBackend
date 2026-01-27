from decimal import Decimal, InvalidOperation
from app.modules.tenant.settings.repository import EmpresaSettingsRepository


class EmpresaSettingsService:
    def __init__(self, repo: EmpresaSettingsRepository):
        self._repo = repo

    def _clean_str(self, v) -> str | None:
        s = str(v or "").strip()
        return s if s else None

    def _clean_url(self, v) -> str | None:
        s = self._clean_str(v)
        if not s:
            return None
        if not (s.startswith("http://") or s.startswith("https://")):
            return None
        if len(s) > 900:
            return None
        return s

    def _clean_moneda(self, v) -> str:
        s = (self._clean_str(v) or "BOB").upper()
        if len(s) > 8:
            return "BOB"
        return s

    def _clean_tasa(self, v) -> Decimal:
        try:
            d = Decimal(str(v).strip() if v is not None else "0")
        except (InvalidOperation, ValueError):
            return Decimal("0")
        if d < 0:
            return Decimal("0")
        if d > 1:
            return Decimal("1")
        return d

    def get_or_create(self, empresa_id: int):
        empresa = self._repo.get_empresa(empresa_id)
        if not empresa:
            return None

        s = self._repo.get_settings(empresa_id)
        if not s:
            s = self._repo.create_default_settings(empresa_id)
            self._repo.save()

        return s

    def get_settings(self, empresa_id: int) -> dict | None:
        s = self.get_or_create(empresa_id)
        if not s:
            return None
        empresa = s.empresa
        d = s.to_dict()
        d["empresa_nombre"] = empresa.nombre if empresa else None
        return d

    def update_settings(self, empresa_id: int, payload: dict) -> dict | None:
        s = self.get_or_create(empresa_id)
        if not s:
            return None

        if "moneda" in payload:
            s.moneda = self._clean_moneda(payload.get("moneda"))

        if "tasa_impuesto" in payload:
            s.tasa_impuesto = self._clean_tasa(payload.get("tasa_impuesto"))

        if "logo_url" in payload:
            s.logo_url = self._clean_url(payload.get("logo_url"))

        if "image_url" in payload:
            s.image_url = self._clean_url(payload.get("image_url"))

        if "descripcion" in payload:
            s.descripcion = self._clean_str(payload.get("descripcion"))

        self._repo.save()
        empresa = s.empresa
        d = s.to_dict()
        d["empresa_nombre"] = empresa.nombre if empresa else None
        return d

    def get_brand(self, empresa_id: int) -> dict | None:
        s = self.get_or_create(empresa_id)
        if not s:
            return None
        empresa = s.empresa
        return {
            "empresa_id": int(empresa_id),
            "empresa_nombre": empresa.nombre if empresa else None,
            "logo_url": s.logo_url,
            "image_url": s.image_url,
            "descripcion": s.descripcion,
            "actualizado_en": s.actualizado_en.isoformat() if s.actualizado_en else None,
        }
