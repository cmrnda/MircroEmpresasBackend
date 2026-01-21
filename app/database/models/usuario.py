from app.extensions import db


class Usuario(db.Model):
    __tablename__ = "usuario"

    usuario_id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())
    ultimo_login = db.Column(db.DateTime(timezone=True))

    platform_admin = db.relationship("UsuarioAdminPlataforma", uselist=False, back_populates="usuario", cascade="all, delete-orphan")
    platform_profile = db.relationship("PlatformAdminProfile", uselist=False, back_populates="usuario", cascade="all, delete-orphan")

    empresas = db.relationship("UsuarioEmpresa", back_populates="usuario", cascade="all, delete-orphan")

    notificaciones = db.relationship("Notificacion", back_populates="usuario")

    def to_dict(self):
        return {
            "usuario_id": int(self.usuario_id),
            "email": self.email,
            "activo": bool(self.activo),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "ultimo_login": self.ultimo_login.isoformat() if self.ultimo_login else None,
        }


class UsuarioAdminPlataforma(db.Model):
    __tablename__ = "usuario_admin_plataforma"

    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="CASCADE"), primary_key=True)

    usuario = db.relationship("Usuario", back_populates="platform_admin")


class PlatformAdminProfile(db.Model):
    __tablename__ = "platform_admin_profile"

    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="CASCADE"), primary_key=True)
    display_name = db.Column(db.Text)
    telefono = db.Column(db.Text)

    usuario = db.relationship("Usuario", back_populates="platform_profile")

    def to_dict(self):
        return {
            "usuario_id": int(self.usuario_id),
            "display_name": self.display_name,
            "telefono": self.telefono,
        }


class UsuarioEmpresa(db.Model):
    __tablename__ = "usuario_empresa"

    empresa_id = db.Column(db.BigInteger, db.ForeignKey("empresa.empresa_id", ondelete="CASCADE"), primary_key=True)
    usuario_id = db.Column(db.BigInteger, db.ForeignKey("usuario.usuario_id", ondelete="CASCADE"), primary_key=True)

    activo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))
    creado_en = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.func.now())

    empresa = db.relationship("Empresa", back_populates="usuarios_empresa")
    usuario = db.relationship("Usuario", back_populates="empresas")

    admin_empresa = db.relationship("UsuarioAdminEmpresa", uselist=False, back_populates="usuario_empresa", cascade="all, delete-orphan")
    vendedor = db.relationship("UsuarioVendedor", uselist=False, back_populates="usuario_empresa", cascade="all, delete-orphan")
    encargado_inventario = db.relationship("UsuarioEncargadoInventario", uselist=False, back_populates="usuario_empresa", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "empresa_id": int(self.empresa_id),
            "usuario_id": int(self.usuario_id),
            "activo": bool(self.activo),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }


class UsuarioAdminEmpresa(db.Model):
    __tablename__ = "usuario_admin_empresa"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario_empresa.empresa_id", "usuario_empresa.usuario_id"],
            ondelete="CASCADE",
        ),
    )

    usuario_empresa = db.relationship("UsuarioEmpresa", back_populates="admin_empresa")


class UsuarioVendedor(db.Model):
    __tablename__ = "usuario_vendedor"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario_empresa.empresa_id", "usuario_empresa.usuario_id"],
            ondelete="CASCADE",
        ),
    )

    usuario_empresa = db.relationship("UsuarioEmpresa", back_populates="vendedor")


class UsuarioEncargadoInventario(db.Model):
    __tablename__ = "usuario_encargado_inventario"

    empresa_id = db.Column(db.BigInteger, primary_key=True)
    usuario_id = db.Column(db.BigInteger, primary_key=True)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["empresa_id", "usuario_id"],
            ["usuario_empresa.empresa_id", "usuario_empresa.usuario_id"],
            ondelete="CASCADE",
        ),
    )

    usuario_empresa = db.relationship("UsuarioEmpresa", back_populates="encargado_inventario")
