from app.extensions import db

class Producto(db.Model):
    __tablename__ = "producto"

    producto_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    categoria_id = db.Column(db.BigInteger, nullable=False)
    codigo = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    stock_min = db.Column(db.Integer, nullable=False, server_default="0")
    activo = db.Column(db.Boolean, nullable=False, server_default="true")

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "codigo", name="uq_producto_empresa_codigo"),
        db.UniqueConstraint("empresa_id", "producto_id", name="uq_producto_empresa_producto_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "categoria_id"],
            ["categoria.empresa_id", "categoria.categoria_id"],
            name="fk_producto_categoria",
        ),
    )
