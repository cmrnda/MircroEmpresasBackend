from app import create_app
from app.extensions import db
from app.db.models.usuario import Usuario
from app.db.models.usuario import UsuarioAdminPlataforma
from app.security.passwords import hash_password

EMAIL = "breakglass@platform.com"
PASSWORD = "BreakGlass_ChangeMe_12345"

def main():
    app = create_app()
    with app.app_context():
        u = Usuario.query.filter_by(email=EMAIL).first()
        if not u:
            u = Usuario(email=EMAIL, password_hash=hash_password(PASSWORD), activo=True)
            db.session.add(u)
            db.session.flush()

        exists = UsuarioAdminPlataforma.query.filter_by(usuario_id=u.usuario_id).first()
        if not exists:
            db.session.add(UsuarioAdminPlataforma(usuario_id=u.usuario_id))

        db.session.commit()
        print("OK platform admin:", EMAIL, "usuario_id:", u.usuario_id)

if __name__ == "__main__":
    main()
