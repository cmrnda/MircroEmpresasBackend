from app.extensions import db


class EmpresaSettings(db.Model):
    __tablename__ = "empresa_settings"

    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), primary_key=True)

    moneda = db.Column(db.Text, nullable=False, server_default="BOB")
    tasa_impuesto = db.Column(db.Numeric(6, 3), nullable=False, server_default="0")

    logo_url = db.Column(db.Text)
    image_url = db.Column(db.Text)
    descripcion = db.Column(db.Text)

    plan_id = db.Column(db.BigInteger, db.ForeignKey("plan.plan_id"))
    suscripcion_estado = db.Column(db.Text, nullable=False, server_default="INACTIVA")
    suscripcion_inicio = db.Column(db.Date)
    suscripcion_fin = db.Column(db.Date)
    suscripcion_renovacion = db.Column(db.Date)

    ultimo_pago_monto = db.Column(db.Numeric(12, 2))
    ultimo_pago_moneda = db.Column(db.Text, server_default="BOB")
    ultimo_pago_metodo = db.Column(db.Text)
    ultimo_pago_referencia_qr = db.Column(db.Text)
    ultimo_pago_estado = db.Column(db.Text)
    ultimo_pagado_en = db.Column(db.DateTime(timezone=True))

    actualizado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    empresa = db.relationship("Empresa", back_populates="settings")
    plan = db.relationship("Plan", back_populates="empresas_settings")

    def to_dict(self):
        return {
            "empresa_id": int(self.empresa_id),
            "moneda": self.moneda,
            "tasa_impuesto": float(self.tasa_impuesto) if self.tasa_impuesto is not None else 0.0,
            "logo_url": self.logo_url,
            "image_url": self.image_url,
            "descripcion": self.descripcion,
            "plan_id": int(self.plan_id) if self.plan_id is not None else None,
            "suscripcion_estado": self.suscripcion_estado,
            "suscripcion_inicio": self.suscripcion_inicio.isoformat() if self.suscripcion_inicio else None,
            "suscripcion_fin": self.suscripcion_fin.isoformat() if self.suscripcion_fin else None,
            "suscripcion_renovacion": self.suscripcion_renovacion.isoformat() if self.suscripcion_renovacion else None,
            "ultimo_pago_monto": float(self.ultimo_pago_monto) if self.ultimo_pago_monto is not None else None,
            "ultimo_pago_moneda": self.ultimo_pago_moneda,
            "ultimo_pago_metodo": self.ultimo_pago_metodo,
            "ultimo_pago_referencia_qr": self.ultimo_pago_referencia_qr,
            "ultimo_pago_estado": self.ultimo_pago_estado,
            "ultimo_pagado_en": self.ultimo_pagado_en.isoformat() if self.ultimo_pagado_en else None,
            "actualizado_en": self.actualizado_en.isoformat() if self.actualizado_en else None,
        }
