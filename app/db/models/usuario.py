from datetime import datetime

from ...extensions import db


class Usuario(db.Model):
    __tablename__ = "usuario"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "email", name="uq_usuario_empresa_email"),
        db.UniqueConstraint("empresa_id", "usuario_id", name="uq_usuario_empresa_usuario_id"),
    )

    usuario_id = db.Column(db.BigInteger, primary_key=True)
    empresa_id = db.Column(
        db.BigInteger,
        db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"),
        nullable=False,
    )
    email = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime(timezone=True))


class AdminPlataforma(db.Model):
    __tablename__ = "usuario_admin_plataforma"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario.empresa_id", "usuario.usuario_id"],
            ondelete="CASCADE",
            name="fk_uap_usuario",
        ),
    )

    empresa_id = db.Column(
        db.BigInteger,
        db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"),
        primary_key=True,
    )
    usuario_id = db.Column(db.BigInteger, primary_key=True)


class AdminEmpresa(db.Model):
    __tablename__ = "usuario_admin_empresa"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario.empresa_id", "usuario.usuario_id"],
            ondelete="CASCADE",
            name="fk_uae_usuario",
        ),
    )

    empresa_id = db.Column(
        db.BigInteger,
        db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"),
        primary_key=True,
    )
    usuario_id = db.Column(db.BigInteger, primary_key=True)


class Vendedor(db.Model):
    __tablename__ = "usuario_vendedor"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario.empresa_id", "usuario.usuario_id"],
            ondelete="CASCADE",
            name="fk_uv_usuario",
        ),
    )

    empresa_id = db.Column(
        db.BigInteger,
        db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"),
        primary_key=True,
    )
    usuario_id = db.Column(db.BigInteger, primary_key=True)
