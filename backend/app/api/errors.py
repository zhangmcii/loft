from app.exceptions import ValidationError
from . import api
from ..utils.response import bad_request, unauthorized, forbidden
from .. import logger


# 这些函数已经在response.py中定义，不再需要在这里重复定义


@api.errorhandler(ValidationError)
def validation_error(e):
    logger.get_logger().warning(f"验证错误: {e.args[0]}")
    return bad_request(message=e.args[0])

