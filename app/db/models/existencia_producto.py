from app.extensions import db

class ExistenciaProducto(db.Model):
    __tablename__ = "existencia_producto"

    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), primary_key=True)
    producto_id = db.Column(db.BigInteger, primary_key=True)
    cantidad_actual = db.Column(db.Numeric(12, 3), nullable=False, server_default="0")

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "producto_id"],
            ["producto.empresa_id", "producto.producto_id"],
            ondelete="CASCADE",
            name="fk_existencia_producto_producto",
        ),
    )
