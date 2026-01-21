"""
认证路由模块
"""
import logging

from flask import current_app, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    jwt_required,
)

from .. import db
from .. import redis as jwt_redis_blocklist
from ..api.upload import get_random_user_avatars
from ..decorators import admin_required
from ..models import User
from ..mycelery.tasks import send_email
from ..schemas import (
    BindEmailRequest,
    ChangeEmailRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    RegisterRequest,
)
from ..utils.response import error, success, unauthorized
from ..utils.time_util import DateUtils
from ..utils.validation import validate_json
from . import auth
from .third_party_login import get_oauth_providers, oauth_callback, oauth_login


@auth.before_app_request
@jwt_required(optional=True, verify_type=False)
def before_request():
    if current_user:
        current_user.ping()
        # if (not current_user.confirmed and request.endpoint
        #         and request.blueprint != 'auth' and request.endpoint != 'static'):
        #     return '用户邮件未认证'


@auth.route("/login", methods=["post"])
def login():
    j = request.get_json()
    user = User.query.filter_by(username=j.get("uiAccountName")).one_or_none()
    if user and user.verify_password(j.get("uiPassword")):
        # 创建新鲜令牌
        fresh_access_token = "Bearer " + create_access_token(identity=user, fresh=True)
        refresh_token = "Bearer " + create_refresh_token(identity=user)
        user.ping()
        return success(
            data=user.to_json(),
            access_token=fresh_access_token,
            refresh_token=refresh_token,
        )
    return error(code=400, message="账号或密码错误")


@auth.route("/register", methods=["POST"])
@validate_json(RegisterRequest)
def register(validated_data):
    # 检查用户名是否已存在
    u = User.query.filter_by(username=validated_data.username).first()
    if u:
        return error(message="该用户名已被注册，请换一个")

    # 检查邮箱是否已存在
    if validated_data.email:
        existing_email = User.query.filter_by(email=validated_data.email).first()
        if existing_email:
            return error(message="该邮箱已被注册，请换一个")

    email = validated_data.email if validated_data.email else None
    random_image = (
        "" if os.getenv("FLASK_CONFIG") == "testing" else get_random_user_avatars()
    )
    logging.info(f"随机图像为：{random_image}")
    user = User(
        email=email,
        username=validated_data.username,
        password=validated_data.password,
        image=random_image,
    )
    db.session.add(user)
    db.session.commit()
    return success()


@auth.route("/applyCode", methods=["POST"])
@jwt_required(optional=True)
@DateUtils.record_time
def apply_code():
    email = request.get_json().get("email")
    code = User.generate_code(email)
    if current_user:
        username = (
            current_user.nickname if current_user.nickname else current_user.username
        )
    else:
        user = User.query.filter_by(email=email).first()
        if not user:
            return error(code=400, message="您输入的邮箱未绑定过账号")
        username = user.nickname if user.nickname else user.username
    # celery发送邮件
    send_email.delay(
        email,
        "Confirm Your Account",
        "code_email.html",
        username=username,
        code=code,
        year=DateUtils.get_year(),
    )
    return success()


@auth.route("/confirm", methods=["POST"])
@jwt_required()
@validate_json(BindEmailRequest)
def confirm(validated_data):
    """绑定邮箱"""
    email = validated_data.email
    code = validated_data.code

    if current_user.email and email != current_user.email:
        return error(message="输入的邮件与用户的邮件不一致")
    if current_user.confirm(email, code):
        db.session.commit()
        return success(
            data={"isConfirmed": current_user.confirmed, "roleId": current_user.role_id}
        )
    return error(message="绑定失败")


@auth.route("/changeEmail", methods=["POST"])
@jwt_required(fresh=True)
@validate_json(ChangeEmailRequest)
def change_email(validated_data):
    """更换邮箱"""
    email = validated_data.new_email
    code = validated_data.code
    password = validated_data.password

    if User.query.filter_by(email=email).first():
        return error(message="填写的邮箱已经存在")
    if current_user.email == email:
        return error(message="请更换新的邮箱地址")

    # 密码
    if not current_user.verify_password(password):
        return error(message="密码错误")
    # 验证码
    if current_user.change_email(email, code):
        db.session.commit()
        return success()
    return error(message="验证码错误")


@auth.route("/changePassword", methods=["POST"])
@jwt_required(fresh=True)
@validate_json(ChangePasswordRequest)
def change_password(validated_data):
    if current_user.verify_password(validated_data.old_password):
        current_user.password = validated_data.new_password
        db.session.commit()
        return success()
    return error(message="原密码错误")


@auth.route("/resetPassword", methods=["POST"])
@validate_json(ForgotPasswordRequest)
def reset_password(validated_data):
    email = validated_data.email
    code = validated_data.code
    password = validated_data.new_password

    # 验证码
    if User.compare_code(email, code):
        user = User.query.filter_by(email=email).first()
        if not user:
            return error(message="此邮箱尚未绑定")
        user.password = password
        db.session.commit()
        return success()
    return error(message="验证码错误")


@auth.route("/helpChangePassword", methods=["POST"])
@admin_required
@jwt_required()
def change_password_admin():
    username = request.get_json().get("username")
    new_password = request.get_json().get("newPassword")
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = new_password
        db.session.commit()
        return success()
    return error(message="用户不存在")


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """刷新token"""
    access_token = "Bearer " + create_access_token(identity=current_user)
    return success(data={"access_token": access_token})


@auth.route("/revokeToken", methods=["DELETE"])
@jwt_required(verify_type=False)
def revoke_token():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    jwt_redis_blocklist.set(jti, "", ex=current_app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    return success(message=f"{ttype.capitalize()} token successfully revoked")


@auth.route("/access_token_test")
@jwt_required()
def _test_access_token():
    """单元测试访问令牌"""
    return success(message="这是access_token_test接口")


@auth.route("/refresh_token_test")
@jwt_required(refresh=True)
def _test_refresh_token():
    """单元测试刷新令牌"""
    return success(message="这是refresh_token_test接口")


@auth.route("/checkFreshness", methods=["GET"])
@jwt_required()
def check_freshness():
    """检测当前令牌是否为新鲜令牌"""
    jwt_data = get_jwt()
    if jwt_data.get("fresh", False):
        return success(message="令牌新鲜")
    return unauthorized(message="该操作需要重新登录以验证身份")


# ==================== OAuth 第三方登录路由 ====================


@auth.route("/oauth/providers", methods=["GET"])
def oauth_providers():
    """获取可用的 OAuth 提供商列表"""
    return get_oauth_providers()


@auth.route("/oauth/<provider>/login", methods=["GET"])
def oauth_login_route(provider):
    """OAuth 登录 - 重定向到第三方授权页面"""
    return oauth_login(provider)


@auth.route("/oauth/<provider>/callback", methods=["GET"])
def oauth_callback_route(provider):
    """OAuth 回调 - 重定向到前端回调页面"""
    # 重定向到前端回调页面，带上所有查询参数
    from flask import url_for

    callback_url = f"/oauth/callback/{provider}?{request.query_string.decode()}"
    return redirect(callback_url)


@auth.route("/oauth/<provider>/callback-api", methods=["GET", "POST"])
def oauth_callback_api_route(provider):
    """OAuth 回调 API - 前端回调页面调用此接口处理登录"""
    from .third_party_login import oauth_callback_api

    return oauth_callback_api(provider)
