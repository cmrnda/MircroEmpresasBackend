from datetime import date
from flask import jsonify
from app.modules.tenants.repository import TenantsRepository
from app.security.password import hash_password

class TenantsService:
    def __init__(self):
        self._repo = TenantsRepository()

    def create_tenant_with_admin(self, data):
        empresa = data.get("empresa") or {}
        admin = data.get("admin") or {}
        config = data.get("config") or {}

        nombre = empresa.get("nombre")
        nit = empresa.get("nit")
        admin_email = admin.get("email")
        admin_password = admin.get("password")

        if not nombre or not admin_email or not admin_password:
            return jsonify({"error": "fields_required"}), 400

        if self._repo.user_email_exists(admin_email):
            return jsonify({"error": "email_already_exists"}), 409

        pw_hash = hash_password(admin_password)
        result = self._repo.create_tenant_with_admin(nombre, nit, config, admin_email, pw_hash)
        return jsonify(result), 201

    def list_tenants(self):
        rows = self._repo.list_tenants()
        return jsonify({"data": rows}), 200

    def get_tenant(self, empresa_id: int):
        row = self._repo.get_tenant(empresa_id)
        if not row:
            return jsonify({"error": "not_found"}), 404
        return jsonify(row), 200

    def set_tenant_status(self, empresa_id: int, data):
        estado = data.get("estado")
        if not estado:
            return jsonify({"error": "estado_required"}), 400
        ok = self._repo.set_tenant_status(empresa_id, str(estado))
        if not ok:
            return jsonify({"error": "not_found"}), 404
        return jsonify({"ok": True}), 200

    def list_plans(self):
        rows = self._repo.list_plans()
        return jsonify({"data": rows}), 200

    def create_plan(self, data):
        nombre = data.get("nombre")
        precio = data.get("precio", 0)
        periodo_cobro = data.get("periodo_cobro")
        if not nombre or not periodo_cobro:
            return jsonify({"error": "fields_required"}), 400
        row = self._repo.create_plan(nombre, precio, periodo_cobro)
        return jsonify(row), 201

    def create_subscription(self, empresa_id: int, data):
        plan_id = data.get("plan_id")
        estado = data.get("estado")
        inicio = data.get("inicio") or str(date.today())
        fin = data.get("fin")
        renovacion = data.get("renovacion")

        if not plan_id or not estado:
            return jsonify({"error": "fields_required"}), 400
        if not self._repo.empresa_exists(empresa_id):
            return jsonify({"error": "empresa_not_found"}), 404

        row = self._repo.create_subscription(empresa_id, int(plan_id), str(estado), inicio, fin, renovacion)
        return jsonify(row), 201

    def create_subscription_payment(self, empresa_id: int, data):
        suscripcion_id = data.get("suscripcion_id")
        monto = data.get("monto")
        moneda = data.get("moneda", "BOB")
        metodo = data.get("metodo")
        referencia_qr = data.get("referencia_qr")
        estado = data.get("estado")
        pagado_en = data.get("pagado_en")

        if not suscripcion_id or monto is None or not metodo or not estado:
            return jsonify({"error": "fields_required"}), 400
        if not self._repo.empresa_exists(empresa_id):
            return jsonify({"error": "empresa_not_found"}), 404

        row = self._repo.create_subscription_payment(
            empresa_id, int(suscripcion_id), monto, moneda, metodo, referencia_qr, str(estado), pagado_en
        )
        return jsonify(row), 201
