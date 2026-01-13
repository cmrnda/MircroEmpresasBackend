from app.extensions import db

class Usuario(db.Model):
    __tablename__ = "usuario"

    usuario_id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, server_default="true")
    creado_en = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    ultimo_login = db.Column(db.DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "email": self.email,
            "activo": bool(self.activo),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "ultimo_login": self.ultimo_login.isoformat() if self.ultimo_login else None,
        }

class UsuarioAdminPlataforma(db.Model):
    __tablename__ = "usuario_admin_plataforma"

    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="CASCADE"), primary_key=True)

class UsuarioEmpresa(db.Model):
    __tablename__ = "usuario_empresa"

    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), primary_key=True)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="CASCADE"), primary_key=True)
    activo = db.Column(db.Boolean, nullable=False, server_default="true")
    creado_en = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

class UsuarioAdminEmpresa(db.Model):
    __tablename__ = "usuario_admin_empresa"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario_empresa.empresa_id", "usuario_empresa.usuario_id"],
            ondelete="CASCADE",
            name="fk_usuario_admin_empresa_usuario_empresa",
        ),
    )

class UsuarioVendedor(db.Model):
    __tablename__ = "usuario_vendedor"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario_empresa.empresa_id", "usuario_empresa.usuario_id"],
            ondelete="CASCADE",
            name="fk_usuario_vendedor_usuario_empresa",
        ),
    )

class UsuarioEncargadoInventario(db.Model):
    __tablename__ = "usuario_encargado_inventario"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario_empresa.empresa_id", "usuario_empresa.usuario_id"],
            ondelete="CASCADE",
            name="fk_usuario_encargado_inventario_usuario_empresa",
        ),
    )
