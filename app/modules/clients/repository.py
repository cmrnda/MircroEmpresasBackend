from sqlalchemy import text
from app.extensions import db
from app.db.models.cliente import Cliente

class ClientsRepository:
    def list_clients(self, empresa_id: int):
        rows = db.session.execute(
            text("""
                 select cliente_id, nombre_razon, nit_ci, telefono, email, activo, es_generico
                 from cliente
                 where empresa_id = :e
                 order by cliente_id asc
                 """),
            {"e": int(empresa_id)}
        ).mappings().all()
        return [dict(r) for r in rows]

    def create_client(self, empresa_id: int, nombre_razon: str, nit_ci: str, telefono: str, email: str, es_generico: bool):
        c = Cliente(
            empresa_id=empresa_id,
            usuario_id=None,
            nombre_razon=nombre_razon,
            nit_ci=nit_ci,
            telefono=telefono,
            email=email,
            activo=True,
            es_generico=es_generico
        )
        db.session.add(c)
        db.session.commit()
        return {"cliente_id": int(c.cliente_id), "empresa_id": int(c.empresa_id)}

    def update_client(self, empresa_id: int, cliente_id: int, data) -> bool:
        c = db.session.query(Cliente).filter_by(empresa_id=empresa_id, cliente_id=cliente_id).first()
        if not c:
            return False
        if "nombre_razon" in data and data.get("nombre_razon"):
            c.nombre_razon = data.get("nombre_razon")
        if "nit_ci" in data:
            c.nit_ci = data.get("nit_ci")
        if "telefono" in data:
            c.telefono = data.get("telefono")
        if "email" in data:
            c.email = data.get("email")
        db.session.commit()
        return True

    def set_client_active(self, empresa_id: int, cliente_id: int, activo: bool) -> bool:
        c = db.session.query(Cliente).filter_by(empresa_id=empresa_id, cliente_id=cliente_id).first()
        if not c:
            return False
        c.activo = activo
        db.session.commit()
        return True

    def get_client_by_user(self, empresa_id: int, usuario_id: int):
        c = db.session.query(Cliente).filter_by(empresa_id=empresa_id, usuario_id=usuario_id, activo=True).first()
        if not c:
            return None
        return {
            "cliente_id": int(c.cliente_id),
            "empresa_id": int(c.empresa_id),
            "nombre_razon": c.nombre_razon,
            "nit_ci": c.nit_ci,
            "telefono": c.telefono,
            "email": c.email,
            "activo": bool(c.activo),
            "es_generico": bool(c.es_generico)
        }

    def update_client_by_user(self, empresa_id: int, usuario_id: int, data) -> bool:
        c = db.session.query(Cliente).filter_by(empresa_id=empresa_id, usuario_id=usuario_id, activo=True).first()
        if not c:
            return False
        if "nombre_razon" in data and data.get("nombre_razon"):
            c.nombre_razon = data.get("nombre_razon")
        if "nit_ci" in data:
            c.nit_ci = data.get("nit_ci")
        if "telefono" in data:
            c.telefono = data.get("telefono")
        db.session.commit()
        return True
