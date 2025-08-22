from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from . import user_profile
from . import posts
from . import follow
from . import comments
from . import praise
from . import notifications
from . import messages
from . import uploads
from . import tags
from . import logs