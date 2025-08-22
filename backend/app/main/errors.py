from . import main
from .. import jwt
from flask import request, jsonify
from werkzeug.exceptions import TooManyRequests
from ..utils.response import error, unauthorized, forbidden as forbidden_response, not_found as not_found_response
from .. import logger

# 日志
log = logger.get_logger()

# jwt无效的自定义回调
@jwt.unauthorized_loader
def missing_token_callback(error_msg):
    log.warning(f"未授权访问: {request.path}, 错误: {error_msg}")
    return unauthorized("token无效")


@main.app_errorhandler(403)
def forbidden(e):
    log.warning(f"权限不足: {request.path}, 错误: {str(e)}")
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        return forbidden_response("权限不足")
    return forbidden_response("权限不足"), 403


@main.app_errorhandler(404)
def page_not_found(e):
    log.warning(f"404错误: {request.path}")
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        return not_found_response("资源不存在")
    return not_found_response("资源不存在"), 404


@main.app_errorhandler(TooManyRequests)
def handle_429(e):
    log.warning(f"请求频率超限: {request.path}, 错误: {str(e.description)}")
    return jsonify(
        code=429,
        message="请求频率超限",
        data=None
    ), 429


@main.app_errorhandler(500)
def internal_server_error(e):
    log.error(f"服务器内部错误: {request.path}, 错误: {str(e)}", exc_info=True)
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        return error(500, "服务器内部错误")
    return error(500, "服务器内部错误"), 500
