from flask import Blueprint

api = Blueprint('api', __name__)

from . import posts, users, comments, errors, authentication

from .posts_1 import register_bp_api
from .notifications import register_notification_api
register_bp_api(api, 'posts1')
register_notification_api(api, 'notifications')
