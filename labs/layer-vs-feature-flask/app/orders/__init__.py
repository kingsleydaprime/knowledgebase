from flask import Blueprint

bp = Blueprint("orders", __name__, template_folder="templates")

from . import routes  # noqa: E402,F401  (attaches the routes to bp)
