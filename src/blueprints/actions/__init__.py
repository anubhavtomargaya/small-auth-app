from flask import Blueprint

actions_app = Blueprint('action', __name__)

from . import routes