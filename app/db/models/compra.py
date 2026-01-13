from app.extensions import db

class Compra(db.Model):
    __tablename__ = "compra"

    compra_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    proveedor_id = db.Column(db.BigInteger, nullable=False)
    fecha = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    estado = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "compra_id", name="uq_compra_empresa_compra_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "proveedor_id"],
            ["proveedor.empresa_id", "proveedor.proveedor_id"],
            name="fk_compra_proveedor",
        ),
    )
