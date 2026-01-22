from app.extensions import db

class CompraDetalle(db.Model):
    __tablename__ = "compra_detalle"

    compra_detalle_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    compra_id = db.Column(db.BigInteger, nullable=False)
    producto_id = db.Column(db.BigInteger, nullable=False)

    cantidad = db.Column(db.Numeric(12, 3), nullable=False)
    costo_unit = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "compra_detalle_id", name="uq_compra_detalle_empresa_id"),
        db.ForeignKeyConstraint(["empresa_id", "compra_id"], ["compra.empresa_id", "compra.compra_id"], ondelete="CASCADE"),
        db.ForeignKeyConstraint(["empresa_id", "producto_id"], ["producto.empresa_id", "producto.producto_id"]),
        db.CheckConstraint("cantidad > 0", name="ck_compra_detalle_cantidad_gt_0"),
        db.CheckConstraint("costo_unit >= 0", name="ck_compra_detalle_costo_ge_0"),
        db.CheckConstraint("subtotal >= 0", name="ck_compra_detalle_subtotal_ge_0"),
    )

    def to_dict(self):
        return {
            "compra_detalle_id": int(self.compra_detalle_id),
            "empresa_id": int(self.empresa_id),
            "compra_id": int(self.compra_id),
            "producto_id": int(self.producto_id),
            "cantidad": float(self.cantidad) if self.cantidad is not None else 0,
            "costo_unit": float(self.costo_unit) if self.costo_unit is not None else 0,
            "subtotal": float(self.subtotal) if self.subtotal is not None else 0,
        }
