from datetime import datetime

from ...extensions import db


class Usuario(db.Model):
    __tablename__ = "usuario"
    __table_args__ = (
        db.UniqueConstraint("email", name="uq_usuario_email"),
    )

    usuario_id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime(timezone=True))


class AdminPlataforma(db.Model):
    __tablename__ = "usuario_admin_plataforma"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.usuario_id"],
            ondelete="CASCADE",
            name="fk_uap_usuario",
        ),
    )

    usuario_id = db.Column(db.BigInteger, primary_key=True)


class AdminEmpresa(db.Model):
    __tablename__ = "usuario_admin_empresa"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.usuario_id"],
            ondelete="CASCADE",
            name="fk_uae_usuario",
        ),
        db.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresa.empresa_id"],
            ondelete="CASCADE",
            name="fk_uae_empresa",
        ),
    )

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)


class Vendedor(db.Model):
    __tablename__ = "usuario_vendedor"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.usuario_id"],
            ondelete="CASCADE",
            name="fk_uv_usuario",
        ),
        db.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresa.empresa_id"],
            ondelete="CASCADE",
            name="fk_uv_empresa",
        ),
    )

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)
