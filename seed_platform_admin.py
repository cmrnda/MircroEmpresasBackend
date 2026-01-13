from app import create_app
from app.extensions import db
from app.db.models.usuario import Usuario, UsuarioAdminPlataforma
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = "admin@platform.com"
    password = "Admin12345"

    u = Usuario.query.filter_by(email=email).first()
    if not u:
        u = Usuario(email=email, password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.flush()

    ap = UsuarioAdminPlataforma.query.filter_by(usuario_id=u.usuario_id).first()
    if not ap:
        db.session.add(UsuarioAdminPlataforma(usuario_id=u.usuario_id))

    db.session.commit()
    print("ok", email)
