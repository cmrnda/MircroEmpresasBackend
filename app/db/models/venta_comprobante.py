from app.extensions import db

class VentaComprobante(db.Model):
    __tablename__ = "venta_comprobante"

    comprobante_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    venta_id = db.Column(db.BigInteger, nullable=False)
    tipo = db.Column(db.Text, nullable=False)
    numero = db.Column(db.Text, nullable=True)
    url_pdf = db.Column(db.Text, nullable=True)
    emitido_en = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "comprobante_id", name="uq_venta_comp_empresa_comp_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "venta_id"],
            ["venta.empresa_id", "venta.venta_id"],
            ondelete="CASCADE",
            name="fk_venta_comp_venta",
        ),
    )
