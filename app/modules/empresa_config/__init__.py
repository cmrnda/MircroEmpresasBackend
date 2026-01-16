from flask import Blueprint

empresa_config_bp = Blueprint("empresa_config", __name__, url_prefix="/empresa/config")

from . import routes  # noqa
