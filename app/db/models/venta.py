from app.extensions import db

class Venta(db.Model):
    __tablename__ = "venta"

    venta_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    cliente_id = db.Column(db.BigInteger, nullable=False)
    fecha_hora = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    descuento_total = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    estado = db.Column(db.Text, nullable=False)
    confirmado_por_usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id"), nullable=True)
    confirmado_en = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "venta_id", name="uq_venta_empresa_venta_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "cliente_id"],
            ["cliente.empresa_id", "cliente.cliente_id"],
            name="fk_venta_cliente",
        ),
    )
