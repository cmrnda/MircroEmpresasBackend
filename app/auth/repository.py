from datetime import datetime, timezone
from sqlalchemy import text
from app.extensions import db
from app.db.models.usuario import Usuario, AdminPlataforma, UsuarioEmpresa, AdminEmpresa, Vendedor
from app.db.models.empresa import Empresa
from app.db.models.cliente import Cliente
from app.db.models.password_reset import PasswordReset
from app.db.models.token_blocklist import TokenBlocklist


class AuthRepository:
    def get_user_by_email(self, email: str):
        return db.session.query(Usuario).filter(Usuario.email == email).first()

    def create_user(self, email: str, password_hash: str):
        u = Usuario(email=email, password_hash=password_hash, activo=True)
        db.session.add(u)
        db.session.commit()
        return u

    def is_admin_plataforma(self, usuario_id: int) -> bool:
        r = db.session.query(AdminPlataforma).filter_by(usuario_id=usuario_id).first()
        return r is not None

    def empresa_exists(self, empresa_id: int) -> bool:
        r = db.session.query(Empresa).filter_by(empresa_id=empresa_id).first()
        return r is not None

    def list_empresas_usuario(self, usuario_id: int):
        rows = db.session.execute(
            text("""
                 select e.empresa_id, e.nombre
                 from usuario_empresa ue
                          join empresa e on e.empresa_id = ue.empresa_id
                 where ue.usuario_id = :u
                   and ue.activo = true
                 order by e.empresa_id asc
                 """),
            {"u": int(usuario_id)}
        ).mappings().all()
        return [dict(r) for r in rows]

    def list_empresas_cliente(self, usuario_id: int):
        rows = db.session.execute(
            text("""
                 select e.empresa_id, e.nombre
                 from cliente c
                          join empresa e on e.empresa_id = c.empresa_id
                 where c.usuario_id = :u
                   and c.activo = true
                 order by e.empresa_id asc
                 """),
            {"u": int(usuario_id)}
        ).mappings().all()
        return [dict(r) for r in rows]

    def user_has_empresa_access(self, empresa_id: int, usuario_id: int) -> bool:
        r = db.session.query(UsuarioEmpresa).filter_by(empresa_id=empresa_id, usuario_id=usuario_id,
                                                       activo=True).first()
        return r is not None

    def user_is_client_for_empresa(self, empresa_id: int, usuario_id: int) -> bool:
        r = db.session.query(Cliente).filter_by(empresa_id=empresa_id, usuario_id=usuario_id, activo=True).first()
        return r is not None

    def get_roles_for_empresa(self, empresa_id: int, usuario_id: int):
        roles = []
        if self.is_admin_plataforma(usuario_id):
            roles.append("ADMIN_PLATAFORMA")
        if db.session.query(AdminEmpresa).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
            roles.append("ADMIN_EMPRESA")
        if db.session.query(Vendedor).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
            roles.append("VENDEDOR")
        if self.user_is_client_for_empresa(empresa_id, usuario_id):
            roles.append("CLIENTE")
        return roles

    def primary_role(self, roles):
        if "ADMIN_PLATAFORMA" in roles:
            return "ADMIN_PLATAFORMA"
        if "ADMIN_EMPRESA" in roles:
            return "ADMIN_EMPRESA"
        if "VENDEDOR" in roles:
            return "VENDEDOR"
        if "CLIENTE" in roles:
            return "CLIENTE"
        return "USER"

    def upsert_cliente(self, empresa_id: int, usuario_id: int, nombre_razon: str, nit_ci: str, telefono: str,
                       email: str):
        c = db.session.query(Cliente).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first()
        if c:
            c.nombre_razon = nombre_razon
            c.nit_ci = nit_ci
            c.telefono = telefono
            c.email = email
            c.activo = True
        else:
            c = Cliente(
                empresa_id=empresa_id,
                usuario_id=usuario_id,
                nombre_razon=nombre_razon,
                nit_ci=nit_ci,
                telefono=telefono,
                email=email,
                activo=True,
                es_generico=False
            )
            db.session.add(c)
        db.session.commit()
        return c

    def create_password_reset(self, usuario_id: int, token_hash: str, expires_at):
        pr = PasswordReset(usuario_id=usuario_id, token_hash=token_hash, expires_at=expires_at)
        db.session.add(pr)
        db.session.commit()
        return pr

    def consume_password_reset(self, token_hash: str):
        now = datetime.now(timezone.utc)
        pr = (
            db.session.query(PasswordReset)
            .filter(PasswordReset.token_hash == token_hash)
            .filter(PasswordReset.used_at.is_(None))
            .filter(PasswordReset.expires_at > now)
            .order_by(PasswordReset.reset_id.desc())
            .first()
        )
        if not pr:
            return None
        pr.used_at = now
        db.session.commit()
        return pr

    def set_user_password(self, usuario_id: int, password_hash: str):
        u = db.session.query(Usuario).filter_by(usuario_id=usuario_id).first()
        if not u:
            return None
        u.password_hash = password_hash
        db.session.commit()
        return u

    def block_token(self, jti: str, usuario_id: int):
        row = db.session.query(TokenBlocklist).filter_by(jti=jti).first()
        if row:
            return row
        b = TokenBlocklist(jti=jti, usuario_id=usuario_id)
        db.session.add(b)
        db.session.commit()
        return b
