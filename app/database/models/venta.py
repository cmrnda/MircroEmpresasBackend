from app.extensions import db


class Venta(db.Model):
    __tablename__ = "venta"

    venta_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    cliente_id = db.Column(db.BigInteger, nullable=False)

    fecha_hora = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    total = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    descuento_total = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    estado = db.Column(db.Text, nullable=False, server_default="CREADA")

    pago_metodo = db.Column(db.Text)
    pago_monto = db.Column(db.Numeric(12, 2))
    pago_referencia_qr = db.Column(db.Text)
    pago_estado = db.Column(db.Text)
    pagado_en = db.Column(db.DateTime(timezone=True))

    comprobante_tipo = db.Column(db.Text)
    comprobante_numero = db.Column(db.Text)
    comprobante_url_pdf = db.Column(db.Text)
    comprobante_emitido_en = db.Column(db.DateTime(timezone=True))

    envio_departamento = db.Column(db.Text)
    envio_ciudad = db.Column(db.Text)
    envio_zona_barrio = db.Column(db.Text)
    envio_direccion_linea = db.Column(db.Text)
    envio_referencia = db.Column(db.Text)
    envio_telefono_receptor = db.Column(db.Text)
    envio_costo = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    envio_estado = db.Column(db.Text)
    envio_tracking = db.Column(db.Text)
    envio_fecha_despacho = db.Column(db.DateTime(timezone=True))
    envio_fecha_entrega = db.Column(db.DateTime(timezone=True))

    confirmado_por_usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="SET NULL"))
    confirmado_en = db.Column(db.DateTime(timezone=True))

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "venta_id", name="uq_venta_empresa_venta_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "cliente_id"],
            ["cliente_empresa.empresa_id", "cliente_empresa.cliente_id"],
            ondelete="RESTRICT",
        ),
        db.CheckConstraint("total >= 0", name="ck_venta_total"),
        db.CheckConstraint("descuento_total >= 0", name="ck_venta_descuento_total"),
        db.CheckConstraint("envio_costo >= 0", name="ck_venta_envio_costo"),
        db.CheckConstraint("pago_monto is null or pago_monto >= 0", name="ck_venta_pago_monto"),
        db.Index("idx_venta_empresa", "empresa_id"),
        db.Index("idx_venta_cliente", "empresa_id", "cliente_id"),
    )

    empresa = db.relationship("Empresa", back_populates="ventas")

    detalles = db.relationship(
        "VentaDetalle",
        back_populates="venta",
        cascade="all, delete-orphan",
        primaryjoin="and_(Venta.empresa_id==VentaDetalle.empresa_id, Venta.venta_id==VentaDetalle.venta_id)",
        foreign_keys="[VentaDetalle.empresa_id, VentaDetalle.venta_id]",
        overlaps="detalles_venta",
    )

    def to_dict(self):
        return {
            "venta_id": int(self.venta_id),
            "empresa_id": int(self.empresa_id),
            "cliente_id": int(self.cliente_id),
            "fecha_hora": self.fecha_hora.isoformat() if self.fecha_hora else None,
            "total": float(self.total) if self.total is not None else 0.0,
            "descuento_total": float(self.descuento_total) if self.descuento_total is not None else 0.0,
            "estado": self.estado,
            "pago_metodo": self.pago_metodo,
            "pago_monto": float(self.pago_monto) if self.pago_monto is not None else None,
            "pago_referencia_qr": self.pago_referencia_qr,
            "pago_estado": self.pago_estado,
            "pagado_en": self.pagado_en.isoformat() if self.pagado_en else None,
            "comprobante_tipo": self.comprobante_tipo,
            "comprobante_numero": self.comprobante_numero,
            "comprobante_url_pdf": self.comprobante_url_pdf,
            "comprobante_emitido_en": self.comprobante_emitido_en.isoformat() if self.comprobante_emitido_en else None,
            "envio_departamento": self.envio_departamento,
            "envio_ciudad": self.envio_ciudad,
            "envio_zona_barrio": self.envio_zona_barrio,
            "envio_direccion_linea": self.envio_direccion_linea,
            "envio_referencia": self.envio_referencia,
            "envio_telefono_receptor": self.envio_telefono_receptor,
            "envio_costo": float(self.envio_costo) if self.envio_costo is not None else 0.0,
            "envio_estado": self.envio_estado,
            "envio_tracking": self.envio_tracking,
            "envio_fecha_despacho": self.envio_fecha_despacho.isoformat() if self.envio_fecha_despacho else None,
            "envio_fecha_entrega": self.envio_fecha_entrega.isoformat() if self.envio_fecha_entrega else None,
            "confirmado_por_usuario_id": int(self.confirmado_por_usuario_id) if self.confirmado_por_usuario_id is not None else None,
            "confirmado_en": self.confirmado_en.isoformat() if self.confirmado_en else None,
        }


class VentaDetalle(db.Model):
    __tablename__ = "venta_detalle"

    venta_detalle_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    venta_id = db.Column(db.BigInteger, nullable=False)
    producto_id = db.Column(db.BigInteger, nullable=False)

    cantidad = db.Column(db.Numeric(12, 3), nullable=False)
    precio_unit = db.Column(db.Numeric(12, 2), nullable=False)
    descuento = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "venta_detalle_id", name="uq_venta_detalle_empresa_venta_detalle_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "venta_id"],
            ["venta.empresa_id", "venta.venta_id"],
            ondelete="CASCADE",
        ),
        db.ForeignKeyConstraint(
            ["empresa_id", "producto_id"],
            ["producto.empresa_id", "producto.producto_id"],
        ),
        db.CheckConstraint("cantidad > 0", name="ck_venta_detalle_cantidad"),
        db.CheckConstraint("precio_unit >= 0", name="ck_venta_detalle_precio_unit"),
        db.CheckConstraint("descuento >= 0", name="ck_venta_detalle_descuento"),
        db.CheckConstraint("subtotal >= 0", name="ck_venta_detalle_subtotal"),
        db.Index("idx_venta_detalle_venta", "empresa_id", "venta_id"),
    )

    venta = db.relationship(
        "Venta",
        back_populates="detalles",
        primaryjoin="and_(VentaDetalle.empresa_id==Venta.empresa_id, VentaDetalle.venta_id==Venta.venta_id)",
        foreign_keys="[VentaDetalle.empresa_id, VentaDetalle.venta_id]",
        overlaps="detalles_venta",
    )

    producto = db.relationship(
        "Producto",
        back_populates="detalles_venta",
        primaryjoin="and_(VentaDetalle.empresa_id==Producto.empresa_id, VentaDetalle.producto_id==Producto.producto_id)",
        foreign_keys="[VentaDetalle.empresa_id, VentaDetalle.producto_id]",
        overlaps="detalles,venta",
    )

    def to_dict(self):
        return {
            "venta_detalle_id": int(self.venta_detalle_id),
            "empresa_id": int(self.empresa_id),
            "venta_id": int(self.venta_id),
            "producto_id": int(self.producto_id),
            "cantidad": float(self.cantidad) if self.cantidad is not None else 0.0,
            "precio_unit": float(self.precio_unit) if self.precio_unit is not None else 0.0,
            "descuento": float(self.descuento) if self.descuento is not None else 0.0,
            "subtotal": float(self.subtotal) if self.subtotal is not None else 0.0,
        }
