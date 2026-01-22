from app.extensions import db

class Compra(db.Model):
    __tablename__ = "compra"

    compra_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    proveedor_id = db.Column(db.BigInteger, nullable=False)

    fecha_hora = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    total = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    estado = db.Column(db.Text, nullable=False, server_default="CREADA")
    observacion = db.Column(db.Text)

    recibido_por_usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="SET NULL"))
    recibido_en = db.Column(db.DateTime(timezone=True))

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "compra_id", name="uq_compra_empresa_id"),
        db.ForeignKeyConstraint(["empresa_id", "proveedor_id"], ["proveedor.empresa_id", "proveedor.proveedor_id"]),
        db.CheckConstraint("total >= 0", name="ck_compra_total_ge_0"),
        db.CheckConstraint("estado in ('CREADA','RECIBIDA','ANULADA')", name="ck_compra_estado"),
    )

    def to_dict(self):
        return {
            "compra_id": int(self.compra_id),
            "empresa_id": int(self.empresa_id),
            "proveedor_id": int(self.proveedor_id),
            "fecha_hora": self.fecha_hora.isoformat() if self.fecha_hora else None,
            "total": float(self.total) if self.total is not None else 0,
            "estado": self.estado,
            "observacion": self.observacion,
            "recibido_por_usuario_id": int(self.recibido_por_usuario_id) if self.recibido_por_usuario_id else None,
            "recibido_en": self.recibido_en.isoformat() if self.recibido_en else None,
        }
