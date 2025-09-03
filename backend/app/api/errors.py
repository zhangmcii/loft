import logging
from app.exceptions import ValidationError
from . import api
from ..utils.response import bad_request, unauthorized, forbidden




@api.errorhandler(ValidationError)
def validation_error(e):
    logging.warning(f"验证错误: {e.args[0]}")
    return bad_request(message=e.args[0])
