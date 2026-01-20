from flask import Blueprint

bp = Blueprint("orders", __name__, url_prefix="/tenant/orders")
