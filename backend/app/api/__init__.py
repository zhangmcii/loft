from flask import Blueprint

api = Blueprint('api', __name__)

from . import users, errors, authentication, follow

from .posts import register_post_api
from .notifications import register_notification_api
from .user_1 import register_user_api
from .follow import register_follow_api
from .praise import register_praise_api
from .tags import register_tag_api
from .messages import register_message_api
from .logs import register_log_api
from .comments import register_comment_api

register_post_api(api, post_item_url='/posts/<int:id>', post_group_url='/posts')
register_notification_api(api, notification_url='/notifications')
register_user_api(api, user_url='/users1/<int:id>', user_image_url='/users1/<int:id>/image')
register_follow_api(api, follow_url='/users1/<string:username>/follow')
register_praise_api(api, post_praise_url='/posts/<int:post_id>/likes',comment_praise_url='/comments/<int:comment_id>/likes')
register_tag_api(api, tag_user_url='/users/<int:user_id>/tags', tag_url='/tags')
register_message_api(api, message_url='/conversations/<int:user_id>/messages')
register_log_api(api, logs_url='logs')
register_comment_api(api, comment_url='/posts/<int:post_id>/comments', comment_manage_url='/comments/<int:comment_id>' )
