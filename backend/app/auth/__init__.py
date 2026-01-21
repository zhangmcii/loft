from flask import Blueprint

auth = Blueprint("auth", __name__)

from . import third_party_login, views
