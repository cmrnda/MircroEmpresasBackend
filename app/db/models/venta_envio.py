from app.extensions import db

class VentaEnvio(db.Model):
    __tablename__ = "venta_envio"

    envio_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    venta_id = db.Column(db.BigInteger, nullable=False)
    departamento = db.Column(db.Text, nullable=False)
    ciudad = db.Column(db.Text, nullable=False)
    zona_barrio = db.Column(db.Text, nullable=True)
    direccion_linea = db.Column(db.Text, nullable=False)
    referencia = db.Column(db.Text, nullable=True)
    telefono_receptor = db.Column(db.Text, nullable=True)
    costo_envio = db.Column(db.Numeric(12, 2), nullable=False, server_default="0")
    estado_envio = db.Column(db.Text, nullable=False)
    tracking = db.Column(db.Text, nullable=True)
    fecha_despacho = db.Column(db.DateTime(timezone=True), nullable=True)
    fecha_entrega = db.Column(db.DateTime(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "envio_id", name="uq_venta_envio_empresa_envio_id"),
        db.UniqueConstraint("empresa_id", "venta_id", name="uq_venta_envio_empresa_venta_id"),
        db.ForeignKeyConstraint(
            ["empresa_id", "venta_id"],
            ["venta.empresa_id", "venta.venta_id"],
            ondelete="CASCADE",
            name="fk_venta_envio_venta",
        ),
    )
