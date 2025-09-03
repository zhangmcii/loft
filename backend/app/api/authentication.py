from . import api

# from flask_jwt_extended import verify_jwt_in_request
# from ..utils.response import unauthorized
# from flask import request
# import re

# skip_post_pattern = r'^(/api/v1/posts/.*$ | /users/\d+$)'
# skip_pattern = r'^/api/v1/(posts/.*$ | users/\d+$)'
skip_pattern = r"^(/api/v1/posts|/api/v1/users/\d+$|/api/v1/dir_name)"

# 日志


@api.before_request
def auth():
    """
    API认证中间件
    """
    # try:
    #     # 对/api/v1/posts开头的请求放行
    #     if re.match(skip_pattern, request.path):
    #         return
    #     else:
    #         verify_jwt_in_request()
    # except Exception as e:
    #     logging.warning(f"未授权访问: {request.path}, 错误: {str(e)}")
    #     return unauthorized("未授权访问")
    pass
