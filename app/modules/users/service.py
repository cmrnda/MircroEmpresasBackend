from flask import jsonify
from app.modules.users.repository import UsersRepository
from app.security.password import hash_password

class UsersService:
    def __init__(self):
        self._repo = UsersRepository()

    def list_users(self, empresa_id: int):
        rows = self._repo.list_users(empresa_id)
        return jsonify({"data": rows}), 200

    def create_user(self, empresa_id: int, data):
        email = data.get("email")
        password = data.get("password")
        roles = data.get("roles") or ["VENDEDOR"]

        if not email or not password:
            return jsonify({"error": "email_password_required"}), 400

        user = self._repo.get_user_by_email(email)
        if not user:
            pw_hash = hash_password(password)
            user = self._repo.create_user(email, pw_hash)

        self._repo.ensure_membership(empresa_id, user.usuario_id, True)
        self._repo.set_roles(empresa_id, user.usuario_id, roles)

        return jsonify({"ok": True, "usuario_id": int(user.usuario_id)}), 201

    def get_user(self, empresa_id: int, usuario_id: int):
        row = self._repo.get_user_detail(empresa_id, usuario_id)
        if not row:
            return jsonify({"error": "not_found"}), 404
        return jsonify(row), 200

    def set_roles(self, empresa_id: int, usuario_id: int, data):
        roles = data.get("roles")
        if not roles or not isinstance(roles, list):
            return jsonify({"error": "roles_required"}), 400
        if not self._repo.membership_exists(empresa_id, usuario_id):
            return jsonify({"error": "user_not_in_empresa"}), 404
        self._repo.set_roles(empresa_id, usuario_id, roles)
        return jsonify({"ok": True}), 200

    def set_status(self, empresa_id: int, usuario_id: int, data):
        activo = data.get("activo")
        if activo is None:
            return jsonify({"error": "activo_required"}), 400
        ok = self._repo.set_membership_active(empresa_id, usuario_id, bool(activo))
        if not ok:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"ok": True}), 200

    def set_password(self, usuario_id: int, data):
        new_password = data.get("new_password")
        if not new_password:
            return jsonify({"error": "new_password_required"}), 400
        pw_hash = hash_password(new_password)
        ok = self._repo.set_user_password(usuario_id, pw_hash)
        if not ok:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"ok": True}), 200
