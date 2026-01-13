from flask import jsonify
from app.modules.clients.repository import ClientsRepository

class ClientsService:
    def __init__(self):
        self._repo = ClientsRepository()

    def list_clients(self, empresa_id: int):
        rows = self._repo.list_clients(empresa_id)
        return jsonify({"data": rows}), 200

    def create_client(self, empresa_id: int, data):
        nombre_razon = data.get("nombre_razon")
        nit_ci = data.get("nit_ci")
        telefono = data.get("telefono")
        email = data.get("email")
        es_generico = bool(data.get("es_generico", False))

        if not nombre_razon:
            return jsonify({"error": "nombre_razon_required"}), 400

        row = self._repo.create_client(empresa_id, nombre_razon, nit_ci, telefono, email, es_generico)
        return jsonify(row), 201

    def update_client(self, empresa_id: int, cliente_id: int, data):
        ok = self._repo.update_client(empresa_id, cliente_id, data)
        if not ok:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"ok": True}), 200

    def set_client_status(self, empresa_id: int, cliente_id: int, data):
        activo = data.get("activo")
        if activo is None:
            return jsonify({"error": "activo_required"}), 400
        ok = self._repo.set_client_active(empresa_id, cliente_id, bool(activo))
        if not ok:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"ok": True}), 200

    def client_me(self, empresa_id: int, usuario_id: int):
        row = self._repo.get_client_by_user(empresa_id, usuario_id)
        if not row:
            return jsonify({"error": "not_found"}), 404
        return jsonify(row), 200

    def client_me_update(self, empresa_id: int, usuario_id: int, data):
        ok = self._repo.update_client_by_user(empresa_id, usuario_id, data)
        if not ok:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"ok": True}), 200
