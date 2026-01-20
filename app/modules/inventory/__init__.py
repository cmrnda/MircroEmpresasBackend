from flask import Blueprint

bp = Blueprint("inventory", __name__, url_prefix="/tenant/inventory")
