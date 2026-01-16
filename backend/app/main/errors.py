# 日志
import logging

from flask import jsonify, request
from werkzeug.exceptions import TooManyRequests

from .. import jwt
from ..utils.response import error
from ..utils.response import forbidden as forbidden_response
from ..utils.response import not_found as not_found_response
from ..utils.response import unauthorized
from . import main


# jwt无效的自定义回调
# 针对伪造的/错误的token
@jwt.unauthorized_loader
def missing_token_callback(error_msg):
    logging.warning(f"未授权访问: {request.path}, 错误: {error_msg}")
    return unauthorized("token无效")


# 针对token过期
@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    logging.warning(f"token已过期: {jwt_header}, 载荷: {jwt_payload}")
    return unauthorized("身份已过期")


@main.app_errorhandler(403)
def forbidden(e):
    logging.warning(f"权限不足: {request.path}, 错误: {str(e)}")
    return forbidden_response("权限不足"), 403


@main.app_errorhandler(404)
def page_not_found(e):
    logging.warning(f"404错误: {request.path}")
    return not_found_response("资源不存在"), 404


@main.app_errorhandler(TooManyRequests)
def handle_429(e):
    logging.warning(f"请求频率超限: {request.path}, 错误: {str(e.description)}")
    return jsonify(code=429, message="请求频率超限", data=None), 429


@main.app_errorhandler(500)
def internal_server_error(e):
    logging.error(f"服务器内部错误: {request.path}, 错误: {str(e)}", exc_info=True)
    return error(500, "服务器内部错误"), 500
