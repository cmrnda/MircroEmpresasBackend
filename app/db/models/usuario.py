from datetime import datetime
from app.extensions import db

class Usuario(db.Model):
    __tablename__ = "usuario"

    usuario_id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime(timezone=True))

class AdminPlataforma(db.Model):
    __tablename__ = "usuario_admin_plataforma"

    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="CASCADE"), primary_key=True)

class UsuarioEmpresa(db.Model):
    __tablename__ = "usuario_empresa"

    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), primary_key=True)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="CASCADE"), primary_key=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

class AdminEmpresa(db.Model):
    __tablename__ = "usuario_admin_empresa"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario_empresa.empresa_id", "usuario_empresa.usuario_id"],
            ondelete="CASCADE",
            name="fk_admin_empresa_usuario_empresa",
        ),
    )

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)

class Vendedor(db.Model):
    __tablename__ = "usuario_vendedor"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario_empresa.empresa_id", "usuario_empresa.usuario_id"],
            ondelete="CASCADE",
            name="fk_vendedor_usuario_empresa",
        ),
    )

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)
