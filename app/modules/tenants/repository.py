from sqlalchemy import text
from app.extensions import db
from app.db.models.empresa import Empresa, EmpresaConfig
from app.db.models.suscripcion import Plan, Suscripcion, SuscripcionPago
from app.db.models.usuario import Usuario, UsuarioEmpresa, AdminEmpresa

class TenantsRepository:
    def empresa_exists(self, empresa_id: int) -> bool:
        return db.session.query(Empresa).filter_by(empresa_id=empresa_id).first() is not None

    def user_email_exists(self, email: str) -> bool:
        return db.session.query(Usuario).filter(Usuario.email == email).first() is not None

    def create_tenant_with_admin(self, nombre: str, nit: str, config: dict, admin_email: str, password_hash: str):
        e = Empresa(nombre=nombre, nit=nit, estado="ACTIVA")
        db.session.add(e)
        db.session.flush()

        c = EmpresaConfig(
            empresa_id=e.empresa_id,
            moneda=config.get("moneda", "BOB"),
            tasa_impuesto=config.get("tasa_impuesto", 0),
            logo_url=config.get("logo_url")
        )
        db.session.add(c)

        u = Usuario(email=admin_email, password_hash=password_hash, activo=True)
        db.session.add(u)
        db.session.flush()

        ue = UsuarioEmpresa(empresa_id=e.empresa_id, usuario_id=u.usuario_id, activo=True)
        db.session.add(ue)

        ar = AdminEmpresa(empresa_id=e.empresa_id, usuario_id=u.usuario_id)
        db.session.add(ar)

        db.session.commit()
        return {"empresa_id": int(e.empresa_id), "admin_usuario_id": int(u.usuario_id)}

    def list_tenants(self):
        rows = db.session.execute(
            text("select empresa_id, nombre, nit, estado, creado_en from empresa order by empresa_id asc")
        ).mappings().all()
        return [dict(r) for r in rows]

    def get_tenant(self, empresa_id: int):
        row = db.session.execute(
            text("""
                 select e.empresa_id, e.nombre, e.nit, e.estado, e.creado_en,
                        ec.moneda, ec.tasa_impuesto, ec.logo_url, ec.actualizado_en
                 from empresa e
                          left join empresa_config ec on ec.empresa_id = e.empresa_id
                 where e.empresa_id = :e
                     limit 1
                 """),
            {"e": int(empresa_id)}
        ).mappings().first()
        return dict(row) if row else None

    def set_tenant_status(self, empresa_id: int, estado: str) -> bool:
        e = db.session.query(Empresa).filter_by(empresa_id=empresa_id).first()
        if not e:
            return False
        e.estado = estado
        db.session.commit()
        return True

    def list_plans(self):
        rows = db.session.execute(
            text("select plan_id, nombre, precio, periodo_cobro from plan order by plan_id asc")
        ).mappings().all()
        return [dict(r) for r in rows]

    def create_plan(self, nombre: str, precio, periodo_cobro: str):
        p = Plan(nombre=nombre, precio=precio, periodo_cobro=periodo_cobro)
        db.session.add(p)
        db.session.commit()
        return {"plan_id": int(p.plan_id), "nombre": p.nombre, "precio": float(p.precio), "periodo_cobro": p.periodo_cobro}

    def create_subscription(self, empresa_id: int, plan_id: int, estado: str, inicio: str, fin, renovacion):
        s = Suscripcion(
            empresa_id=empresa_id,
            plan_id=plan_id,
            estado=estado,
            inicio=inicio,
            fin=fin,
            renovacion=renovacion
        )
        db.session.add(s)
        db.session.commit()
        return {"suscripcion_id": int(s.suscripcion_id), "empresa_id": int(s.empresa_id), "plan_id": int(s.plan_id), "estado": s.estado}

    def create_subscription_payment(self, empresa_id: int, suscripcion_id: int, monto, moneda: str, metodo: str, referencia_qr: str, estado: str, pagado_en):
        sp = SuscripcionPago(
            empresa_id=empresa_id,
            suscripcion_id=suscripcion_id,
            monto=monto,
            moneda=moneda,
            metodo=metodo,
            referencia_qr=referencia_qr,
            estado=estado,
            pagado_en=pagado_en
        )
        db.session.add(sp)
        db.session.commit()
        return {"pago_suscripcion_id": int(sp.pago_suscripcion_id), "empresa_id": int(sp.empresa_id), "suscripcion_id": int(sp.suscripcion_id), "estado": sp.estado}
