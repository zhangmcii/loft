import logging

from app.exceptions import ValidationError

from ..utils.response import bad_request
from . import api


@api.errorhandler(ValidationError)
def validation_error(e):
    logging.warning(f"验证错误: {e.args[0]}")
    return bad_request(message=e.args[0])
