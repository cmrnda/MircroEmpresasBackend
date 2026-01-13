from typing import List, Optional
from app.extensions import db
from app.db.models.usuario import Usuario, AdminEmpresa, AdminPlataforma, Vendedor

class UsersRepository:
    def get_by_id(self, empresa_id: int, usuario_id: int) -> Optional[Usuario]:
        return Usuario.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first()

    def get_by_email(self, empresa_id: int, email: str) -> Optional[Usuario]:
        return Usuario.query.filter_by(empresa_id=empresa_id, email=email).first()

    def list(self, empresa_id: int) -> List[Usuario]:
        return Usuario.query.filter_by(empresa_id=empresa_id).order_by(Usuario.usuario_id.asc()).all()

    def create(self, user: Usuario) -> Usuario:
        db.session.add(user)
        db.session.commit()
        return user

    def update(self) -> None:
        db.session.commit()

    def delete_roles(self, empresa_id: int, usuario_id: int) -> None:
        AdminPlataforma.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
        AdminEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
        Vendedor.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).delete()
        db.session.commit()

    def add_role(self, empresa_id: int, usuario_id: int, role: str) -> None:
        role = role.upper().strip()

        if role == "ADMIN_PLATAFORMA":
            db.session.add(AdminPlataforma(empresa_id=empresa_id, usuario_id=usuario_id))
        elif role == "ADMIN_EMPRESA":
            db.session.add(AdminEmpresa(empresa_id=empresa_id, usuario_id=usuario_id))
        elif role == "VENDEDOR":
            db.session.add(Vendedor(empresa_id=empresa_id, usuario_id=usuario_id))
        else:
            raise ValueError("INVALID_ROLE")

        db.session.commit()

    def get_roles(self, empresa_id: int, usuario_id: int) -> List[str]:
        roles = []
        if AdminPlataforma.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
            roles.append("ADMIN_PLATAFORMA")
        if AdminEmpresa.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
            roles.append("ADMIN_EMPRESA")
        if Vendedor.query.filter_by(empresa_id=empresa_id, usuario_id=usuario_id).first():
            roles.append("VENDEDOR")
        return roles
