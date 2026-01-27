from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.database.models.empresa import Empresa
from app.database.models.cliente import Cliente, ClienteEmpresa


def _empresa_activa(empresa_id: int) -> bool:
    e = (
        db.session.query(Empresa)
        .filter(Empresa.empresa_id == int(empresa_id))
        .filter(Empresa.estado == "ACTIVA")
        .first()
    )
    return e is not None


def shop_client_register(empresa_id: int, payload: dict):
    if not _empresa_activa(int(empresa_id)):
        return None, "invalid_empresa"

    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    nombre_razon = (payload.get("nombre_razon") or "").strip()

    nit_ci = (payload.get("nit_ci") or "").strip() or None
    telefono = (payload.get("telefono") or "").strip() or None

    if not email or not password or not nombre_razon:
        return None, "invalid_payload"
    if len(password) < 6:
        return None, "weak_password"

    exists = db.session.query(Cliente).filter(Cliente.email == email).first()
    if exists:
        return None, "email_in_use"

    c = Cliente(
        email=email,
        password_hash=generate_password_hash(password),
        nombre_razon=nombre_razon,
        nit_ci=nit_ci,
        telefono=telefono,
        activo=True,
    )
    db.session.add(c)
    db.session.flush()

    ce = ClienteEmpresa(empresa_id=int(empresa_id), cliente_id=int(c.cliente_id), activo=True)
    db.session.add(ce)
    db.session.flush()

    token = create_access_token(
        identity=str(c.cliente_id),
        additional_claims={
            "type": "client",
            "empresa_id": int(empresa_id),
            "cliente_id": int(c.cliente_id),
        },
    )

    return {"access_token": token, "cliente": c.to_dict()}, None


def shop_client_login(empresa_id: int, payload: dict):
    if not _empresa_activa(int(empresa_id)):
        return None, "invalid_empresa"

    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return None, "invalid_payload"

    c = db.session.query(Cliente).filter(Cliente.email == email).filter(Cliente.activo.is_(True)).first()
    if not c:
        return None, "invalid_credentials"

    if not check_password_hash(c.password_hash, password):
        return None, "invalid_credentials"

    ce = (
        db.session.query(ClienteEmpresa)
        .filter(ClienteEmpresa.empresa_id == int(empresa_id))
        .filter(ClienteEmpresa.cliente_id == int(c.cliente_id))
        .filter(ClienteEmpresa.activo.is_(True))
        .first()
    )
    if not ce:
        return None, "forbidden_empresa"

    token = create_access_token(
        identity=str(c.cliente_id),
        additional_claims={
            "type": "client",
            "empresa_id": int(empresa_id),
            "cliente_id": int(c.cliente_id),
        },
    )

    return {"access_token": token, "cliente": c.to_dict()}, None
