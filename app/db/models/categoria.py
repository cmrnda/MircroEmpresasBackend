from app.extensions import db

class Categoria(db.Model):
    __tablename__ = "categoria"

    categoria_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), nullable=False)
    nombre = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, server_default="true")

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "nombre", name="uq_categoria_empresa_nombre"),
        db.UniqueConstraint("empresa_id", "categoria_id", name="uq_categoria_empresa_categoria_id"),
    )
