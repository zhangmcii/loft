import logging

from app.exceptions import ValidationError
from flask import request

from .. import jwt
from .. import redis as jwt_redis_blocklist
from ..utils.response import bad_request, unauthorized
from . import api


@api.errorhandler(ValidationError)
def validation_error(e):
    logging.warning(f"验证错误: {e.args[0]}")
    return bad_request(message=e.args[0])


# jwt无效的自定义回调
@jwt.unauthorized_loader
def missing_token_callback(error_msg):
    """针对伪造的/错误的token"""
    logging.warning(f"未授权访问: {request.path}, 错误: {error_msg}")
    return unauthorized("token无效")


@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    """针对token过期"""
    logging.warning(f"token已过期: {jwt_header}, 载荷: {jwt_payload}")
    return unauthorized("身份已过期")


@jwt.revoked_token_loader
def my_revoked_token_callback(jwt_header, jwt_payload):
    """针对token被撤销"""
    logging.warning(f"token已被撤销")
    return unauthorized("该token已被撤销")


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    """黑名单"""
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None
