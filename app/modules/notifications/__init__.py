from flask import Blueprint

bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

# Importa rutas para que se registren los endpoints
from app.modules.notifications import routes  # noqa: E402,F401
