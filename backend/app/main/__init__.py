from flask import Blueprint

main = Blueprint("main", __name__)

from . import (comments, errors, follow, logs, messages, notifications, posts,
               praise, tags, uploads, user_profile, views)
