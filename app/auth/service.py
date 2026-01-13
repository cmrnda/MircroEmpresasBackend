import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from flask import jsonify
from flask_jwt_extended import create_access_token
from app.auth.repository import AuthRepository
from app.security.password import verify_password, hash_password
from app.config import Config

class AuthService:
    def __init__(self):
        self._repo = AuthRepository()

    def platform_login(self, data):
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"error": "email_password_required"}), 400

        user = self._repo.get_user_by_email(email)
        if not user:
            return jsonify({"error": "invalid_credentials"}), 401
        if not user.activo:
            return jsonify({"error": "user_inactive"}), 403
        if not verify_password(password, user.password_hash):
            return jsonify({"error": "invalid_credentials"}), 401

        if not self._repo.is_admin_plataforma(user.usuario_id):
            return jsonify({"error": "not_platform_admin"}), 403

        roles = ["ADMIN_PLATAFORMA"]
        claims = {
            "usuario_id": int(user.usuario_id),
            "scope": "PLATFORM",
            "empresa_id": None,
            "roles": roles,
            "primary_role": "ADMIN_PLATAFORMA"
        }
        token = create_access_token(identity=str(user.usuario_id), additional_claims=claims)
        return jsonify({"access_token": token, "usuario_id": int(user.usuario_id), "roles": roles, "scope": "PLATFORM"}), 200

    def tenant_login(self, data):
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"error": "email_password_required"}), 400

        user = self._repo.get_user_by_email(email)
        if not user:
            return jsonify({"error": "invalid_credentials"}), 401
        if not user.activo:
            return jsonify({"error": "user_inactive"}), 403
        if not verify_password(password, user.password_hash):
            return jsonify({"error": "invalid_credentials"}), 401

        empresas = self._repo.list_empresas_usuario(user.usuario_id)
        if not empresas:
            return jsonify({"error": "no_tenant_access"}), 403

        if len(empresas) == 1:
            empresa_id = int(empresas[0]["empresa_id"])
            roles = self._repo.get_roles_for_empresa(empresa_id, user.usuario_id)
            if not roles:
                return jsonify({"error": "no_roles_for_empresa"}), 403
            claims = {
                "usuario_id": int(user.usuario_id),
                "scope": "TENANT",
                "empresa_id": empresa_id,
                "roles": roles,
                "primary_role": self._repo.primary_role(roles)
            }
            token = create_access_token(identity=str(user.usuario_id), additional_claims=claims)
            return jsonify({"access_token": token, "empresa_id": empresa_id, "roles": roles, "scope": "TENANT"}), 200

        enriched = []
        for e in empresas:
            empresa_id = int(e["empresa_id"])
            roles = self._repo.get_roles_for_empresa(empresa_id, user.usuario_id)
            enriched.append({"empresa_id": empresa_id, "nombre": e["nombre"], "roles": roles})

        return jsonify({"require_select_empresa": True, "empresas": enriched, "scope": "TENANT"}), 200

    def client_login(self, data):
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"error": "email_password_required"}), 400

        user = self._repo.get_user_by_email(email)
        if not user:
            return jsonify({"error": "invalid_credentials"}), 401
        if not user.activo:
            return jsonify({"error": "user_inactive"}), 403
        if not verify_password(password, user.password_hash):
            return jsonify({"error": "invalid_credentials"}), 401

        empresas = self._repo.list_empresas_cliente(user.usuario_id)
        if not empresas:
            return jsonify({"error": "no_client_access"}), 403

        if len(empresas) == 1:
            empresa_id = int(empresas[0]["empresa_id"])
            roles = ["CLIENTE"]
            claims = {
                "usuario_id": int(user.usuario_id),
                "scope": "CLIENT",
                "empresa_id": empresa_id,
                "roles": roles,
                "primary_role": "CLIENTE"
            }
            token = create_access_token(identity=str(user.usuario_id), additional_claims=claims)
            return jsonify({"access_token": token, "empresa_id": empresa_id, "roles": roles, "scope": "CLIENT"}), 200

        enriched = []
        for e in empresas:
            enriched.append({"empresa_id": int(e["empresa_id"]), "nombre": e["nombre"], "roles": ["CLIENTE"]})

        return jsonify({"require_select_empresa": True, "empresas": enriched, "scope": "CLIENT"}), 200

    def select_empresa(self, claims, data):
        scope = claims.get("scope")
        usuario_id = claims.get("usuario_id")
        empresa_id = data.get("empresa_id")

        if not usuario_id or not scope:
            return jsonify({"error": "invalid_claims"}), 401
        if empresa_id is None:
            return jsonify({"error": "empresa_id_required"}), 400

        empresa_id = int(empresa_id)
        if not self._repo.empresa_exists(empresa_id):
            return jsonify({"error": "empresa_not_found"}), 404

        if scope == "TENANT":
            if not self._repo.user_has_empresa_access(empresa_id, usuario_id):
                return jsonify({"error": "no_tenant_access"}), 403
            roles = self._repo.get_roles_for_empresa(empresa_id, usuario_id)
            if not roles:
                return jsonify({"error": "no_roles_for_empresa"}), 403
            new_claims = {
                "usuario_id": int(usuario_id),
                "scope": "TENANT",
                "empresa_id": empresa_id,
                "roles": roles,
                "primary_role": self._repo.primary_role(roles)
            }
            token = create_access_token(identity=str(usuario_id), additional_claims=new_claims)
            return jsonify({"access_token": token, "empresa_id": empresa_id, "roles": roles, "scope": "TENANT"}), 200

        if scope == "CLIENT":
            if not self._repo.user_is_client_for_empresa(empresa_id, usuario_id):
                return jsonify({"error": "no_client_access"}), 403
            roles = ["CLIENTE"]
            new_claims = {
                "usuario_id": int(usuario_id),
                "scope": "CLIENT",
                "empresa_id": empresa_id,
                "roles": roles,
                "primary_role": "CLIENTE"
            }
            token = create_access_token(identity=str(usuario_id), additional_claims=new_claims)
            return jsonify({"access_token": token, "empresa_id": empresa_id, "roles": roles, "scope": "CLIENT"}), 200

        return jsonify({"error": "select_empresa_not_allowed"}), 403

    def client_signup(self, empresa_id_header, data):
        if not empresa_id_header:
            return jsonify({"error": "empresa_required_header"}), 400

        try:
            empresa_id = int(empresa_id_header)
        except Exception:
            return jsonify({"error": "empresa_invalid"}), 400

        if not self._repo.empresa_exists(empresa_id):
            return jsonify({"error": "empresa_not_found"}), 404

        email = data.get("email")
        password = data.get("password")
        nombre_razon = data.get("nombre_razon")
        nit_ci = data.get("nit_ci")
        telefono = data.get("telefono")

        if not email or not password or not nombre_razon:
            return jsonify({"error": "fields_required"}), 400

        existing = self._repo.get_user_by_email(email)
        if existing:
            user = existing
        else:
            pw_hash = hash_password(password)
            user = self._repo.create_user(email, pw_hash)

        self._repo.upsert_cliente(empresa_id, user.usuario_id, nombre_razon, nit_ci, telefono, email)
        return jsonify({"ok": True, "empresa_id": empresa_id, "usuario_id": int(user.usuario_id)}), 201

    def password_request(self, data):
        email = data.get("email")
        if not email:
            return jsonify({"error": "email_required"}), 400

        user = self._repo.get_user_by_email(email)
        if not user:
            return jsonify({"ok": True}), 200

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=Config.reset_token_minutes())
        self._repo.create_password_reset(user.usuario_id, token_hash, expires_at)
        return jsonify({"ok": True, "reset_token": token}), 200

    def password_reset(self, data):
        token = data.get("token")
        new_password = data.get("new_password")
        if not token or not new_password:
            return jsonify({"error": "token_new_password_required"}), 400

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        pr = self._repo.consume_password_reset(token_hash)
        if not pr:
            return jsonify({"error": "invalid_or_expired_token"}), 400

        pw_hash = hash_password(new_password)
        self._repo.set_user_password(pr.usuario_id, pw_hash)
        return jsonify({"ok": True}), 200

    def logout(self, claims):
        jti = claims.get("jti")
        usuario_id = claims.get("usuario_id")
        if not jti or not usuario_id:
            return jsonify({"error": "invalid_claims"}), 400
        self._repo.block_token(str(jti), int(usuario_id))
        return jsonify({"ok": True}), 200
