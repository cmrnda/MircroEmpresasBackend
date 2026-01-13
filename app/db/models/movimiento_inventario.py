from app.extensions import db

class MovimientoInventario(db.Model):
    __tablename__ = "movimiento_inventario"

    movimiento_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    producto_id = db.Column(db.BigInteger, nullable=False)
    tipo = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Numeric(12, 3), nullable=False)
    ref_tabla = db.Column(db.Text, nullable=True)
    ref_id = db.Column(db.BigInteger, nullable=True)
    fecha = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    realizado_por_usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "movimiento_id", name="uq_mov_inv_empresa_mov_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "producto_id"],
            ["producto.empresa_id", "producto.producto_id"],
            name="fk_movimiento_producto",
        ),
    )
