from flask import Blueprint

api = Blueprint('api', __name__)

from . import users, errors, authentication, follow

from .posts_1 import register_bp_api
from .notifications import register_notification_api
from .user_1 import register_user_api
from .follow import register_follow_api
from .praise import register_praise_api
from .tags import register_tag_api
from .messages import register_message_api
from .logs import register_log_api
from .comments_1 import register_comment_api

register_bp_api(api, 'posts1')
register_notification_api(api, 'notifications')
register_user_api(api, 'users1')
register_follow_api(api, 'users1')
register_praise_api(api, 'likes')
register_tag_api(api, 'tags')
register_message_api(api, 'messages')
register_log_api(api, 'logs')
register_comment_api(api, 'comments')
