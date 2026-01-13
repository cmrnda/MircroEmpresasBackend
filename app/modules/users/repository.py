from sqlalchemy import text
from app.extensions import db
from app.db.models.usuario import Usuario, UsuarioEmpresa, AdminEmpresa, Vendedor

class UsersRepository:
    def get_user_by_email(self, email: str):
        return db.session.query(Usuario).filter(Usuario.email == email).first()

    def create_user(self, email: str, password_hash: str):
        u = Usuario(email=email, password_hash=password_hash, activo=True)
        db.session.add(u)
        db.session.commit()
        return u

    def ensure_membership(self, empresa_id: int, usuario_id: int, activo: bool):
        ue = db.session.query(UsuarioEmpresa).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first()
        if ue:
            ue.activo = activo
        else:
            ue = UsuarioEmpresa(empresa_id=empresa_id, usuario_id=usuario_id, activo=activo)
            db.session.add(ue)
        db.session.commit()
        return ue

    def membership_exists(self, empresa_id: int, usuario_id: int) -> bool:
        ue = db.session.query(UsuarioEmpresa).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first()
        return ue is not None

    def set_membership_active(self, empresa_id: int, usuario_id: int, activo: bool) -> bool:
        ue = db.session.query(UsuarioEmpresa).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first()
        if not ue:
            return False
        ue.activo = activo
        db.session.commit()
        return True

    def delete_roles(self, empresa_id: int, usuario_id: int):
        db.session.query(AdminEmpresa).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
        db.session.query(Vendedor).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
        db.session.commit()

    def set_roles(self, empresa_id: int, usuario_id: int, roles):
        self.delete_roles(empresa_id, usuario_id)
        normalized = [str(r).upper().strip() for r in roles]
        for r in normalized:
            if r == "ADMIN_EMPRESA":
                db.session.add(AdminEmpresa(empresa_id=empresa_id, usuario_id=usuario_id))
            elif r == "VENDEDOR":
                db.session.add(Vendedor(empresa_id=empresa_id, usuario_id=usuario_id))
        db.session.commit()

    def get_roles(self, empresa_id: int, usuario_id: int):
        roles = []
        if db.session.query(AdminEmpresa).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
            roles.append("ADMIN_EMPRESA")
        if db.session.query(Vendedor).filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
            roles.append("VENDEDOR")
        return roles

    def list_users(self, empresa_id: int):
        rows = db.session.execute(
            text("""
                 select u.usuario_id, u.email, u.activo as activo_global,
                        ue.activo as activo_empresa
                 from usuario_empresa ue
                          join usuario u on u.usuario_id = ue.usuario_id
                 where ue.empresa_id = :e
                 order by u.usuario_id asc
                 """),
            {"e": int(empresa_id)}
        ).mappings().all()

        data = []
        for r in rows:
            usuario_id = int(r["usuario_id"])
            roles = self.get_roles(empresa_id, usuario_id)
            data.append({
                "usuario_id": usuario_id,
                "email": r["email"],
                "activo_global": bool(r["activo_global"]),
                "activo_empresa": bool(r["activo_empresa"]),
                "roles": roles
            })
        return data

    def get_user_detail(self, empresa_id: int, usuario_id: int):
        row = db.session.execute(
            text("""
                 select u.usuario_id, u.email, u.activo as activo_global,
                        ue.activo as activo_empresa
                 from usuario_empresa ue
                          join usuario u on u.usuario_id = ue.usuario_id
                 where ue.empresa_id = :e and u.usuario_id = :u
                     limit 1
                 """),
            {"e": int(empresa_id), "u": int(usuario_id)}
        ).mappings().first()
        if not row:
            return None
        roles = self.get_roles(empresa_id, int(row["usuario_id"]))
        return {
            "usuario_id": int(row["usuario_id"]),
            "email": row["email"],
            "activo_global": bool(row["activo_global"]),
            "activo_empresa": bool(row["activo_empresa"]),
            "roles": roles
        }

    def set_user_password(self, usuario_id: int, password_hash: str) -> bool:
        u = db.session.query(Usuario).filter_by(usuario_id=usuario_id).first()
        if not u:
            return False
        u.password_hash = password_hash
        db.session.commit()
        return True
