from typing import Dict, List
from app.db.models.usuario import Usuario
from app.modules.users.repository import UsersRepository
from app.security.password import hash_password

class UsersService:
    def __init__(self) -> None:
        self._repo = UsersRepository()

    def create_user(self, empresa_id: int, email: str, password: str, roles: List[str]) -> Dict:
        existing = self._repo.get_by_email(empresa_id, email)
        if existing:
            raise ValueError("EMAIL_EXISTS")

        user = Usuario(
            empresa_id=empresa_id,
            email=email,
            password_hash=hash_password(password),
            activo=True,
        )
        self._repo.create(user)

        self._repo.delete_roles(empresa_id, user.usuario_id)
        for r in roles:
            self._repo.add_role(empresa_id, user.usuario_id, r)

        return self._to_dto(empresa_id, user)

    def list_users(self, empresa_id: int) -> List[Dict]:
        users = self._repo.list(empresa_id)
        return [self._to_dto(empresa_id, u) for u in users]

    def get_user(self, empresa_id: int, usuario_id: int) -> Dict:
        user = self._repo.get_by_id(empresa_id, usuario_id)
        if not user:
            raise ValueError("NOT_FOUND")
        return self._to_dto(empresa_id, user)

    def update_user(self, empresa_id: int, usuario_id: int, email: str | None, activo: bool | None) -> Dict:
        user = self._repo.get_by_id(empresa_id, usuario_id)
        if not user:
            raise ValueError("NOT_FOUND")

        if email and email != user.email:
            if self._repo.get_by_email(empresa_id, email):
                raise ValueError("EMAIL_EXISTS")
            user.email = email

        if activo is not None:
            user.activo = activo

        self._repo.update()
        return self._to_dto(empresa_id, user)

    def set_roles(self, empresa_id: int, usuario_id: int, roles: List[str]) -> Dict:
        user = self._repo.get_by_id(empresa_id, usuario_id)
        if not user:
            raise ValueError("NOT_FOUND")

        self._repo.delete_roles(empresa_id, usuario_id)
        for r in roles:
            self._repo.add_role(empresa_id, usuario_id, r)

        return self._to_dto(empresa_id, user)

    def change_password(self, empresa_id: int, usuario_id: int, new_password: str) -> Dict:
        user = self._repo.get_by_id(empresa_id, usuario_id)
        if not user:
            raise ValueError("NOT_FOUND")

        user.password_hash = hash_password(new_password)
        self._repo.update()
        return self._to_dto(empresa_id, user)

    def _to_dto(self, empresa_id: int, user: Usuario) -> Dict:
        roles = self._repo.get_roles(empresa_id, user.usuario_id)
        return {
            "usuario_id": user.usuario_id,
            "empresa_id": user.empresa_id,
            "email": user.email,
            "activo": user.activo,
            "roles": roles,
            "creado_en": user.creado_en.isoformat() if user.creado_en else None,
            "ultimo_login": user.ultimo_login.isoformat() if user.ultimo_login else None,
        }
