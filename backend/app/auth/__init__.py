from flask import Blueprint

auth = Blueprint("auth", __name__)

from . import third_party_login, views

# 注册第三方登录 Blueprint（注册到 auth blueprint 下）
auth.register_blueprint(third_party_login.auth_bp, url_prefix="/bp")
