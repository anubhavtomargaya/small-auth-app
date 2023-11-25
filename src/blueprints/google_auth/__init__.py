from flask import Blueprint

google_auth = Blueprint('google_auth', __name__)

from . import routes