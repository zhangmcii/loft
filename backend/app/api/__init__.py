from flask import Blueprint

api = Blueprint('api', __name__)

from . import posts, users, comments, errors, authentication

from .posts_1 import register_bp_api
register_bp_api(api, 'posts1')
