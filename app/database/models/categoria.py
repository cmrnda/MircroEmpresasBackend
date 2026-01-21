from app.extensions import db


class Categoria(db.Model):
    __tablename__ = "categoria"

    categoria_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)

    nombre = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "nombre", name="uq_categoria_empresa_nombre"),
        db.UniqueConstraint("empresa_id", "categoria_id", name="uq_categoria_empresa_categoria_id"),
        db.Index("idx_categoria_empresa", "empresa_id"),
    )

    empresa = db.relationship("Empresa", back_populates="categorias")
    productos = db.relationship("Producto", back_populates="categoria")

    def to_dict(self):
        return {
            "categoria_id": int(self.categoria_id),
            "empresa_id": int(self.empresa_id),
            "nombre": self.nombre,
            "activo": bool(self.activo),
        }
