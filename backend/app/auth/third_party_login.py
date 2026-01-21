"""
第三方登录模块
支持 GitHub 等第三方平台的 OAuth 登录
"""
import logging
import os

import requests
from flask import Blueprint, current_app, request
from flask_jwt_extended import create_access_token, create_refresh_token

from .. import db
from ..models import ThirdPartyAccount, User
from ..utils.response import error, success

# 创建 Blueprint
auth_bp = Blueprint("auth_bp", __name__)

# GitHub OAuth 配置
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
# 前端页面地址
GITHUB_REDIRECT_URI = os.getenv(
    "GITHUB_REDIRECT_URI", "http://127.0.0.1:5173/callback/github"
)
GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_API_URL = "https://api.github.com/user"


@auth_bp.route("/github/authorize", methods=["GET"])
def github_authorize():
    """
    获取 GitHub 授权 URL
    前端直接跳转到该 URL
    """
    if not GITHUB_CLIENT_ID:
        logging.error("GitHub OAuth 未配置 client_id")
        return error(code=500, message="GitHub OAuth 配置错误")

    # GitHub 授权 URL 参数
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "user:email",
        "response_type": "code",
        "state": "github_auth",  # 简单的 CSRF 防护
    }

    # 构建授权 URL
    from urllib.parse import urlencode

    auth_url = f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"

    return success(data={"auth_url": auth_url})


@auth_bp.route("/github/callback", methods=["GET"])
def github_callback():
    """
    GitHub OAuth 回调处理
    1. 获取授权码，换取 access_token
    2. 使用 access_token 获取用户信息
    3. 查询或创建用户及第三方账号记录
    4. 返回 JWT token
    """
    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        logging.warning("GitHub OAuth 回调缺少 code 参数")
        return error(code=400, message="授权失败: 缺少授权码")

    try:
        # 1. 使用授权码换取 access_token
        token_data = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": GITHUB_REDIRECT_URI,
        }

        token_response = requests.post(
            GITHUB_ACCESS_TOKEN_URL,
            data=token_data,
            headers={"Accept": "application/json"},
        )
        token_response.raise_for_status()
        token_json = token_response.json()

        access_token = token_json.get("access_token")
        if not access_token:
            logging.error(f"GitHub OAuth 获取 access_token 失败: {token_json}")
            return error(code=400, message="获取访问令牌失败")

        # 2. 使用 access_token 获取用户信息
        user_response = requests.get(
            GITHUB_USER_API_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        user_response.raise_for_status()
        user_info = user_response.json()

        # GitHub 用户信息
        github_id = str(user_info.get("id"))  # 使用 GitHub ID 作为 openid
        github_login = user_info.get("login")
        github_name = user_info.get("name") or github_login
        github_avatar = user_info.get("avatar_url")
        github_email = user_info.get("email")
        github_bio = user_info.get("bio")
        github_location = user_info.get("location")

        logging.info(
            f"GitHub 用户信息: id={github_id}, login={github_login}, email={github_email}"
        )

        # 3. 查询第三方账号记录
        third_party_account = ThirdPartyAccount.query.filter_by(
            provider="github", openid=github_id
        ).first()

        if third_party_account:
            # 已存在：更新快照信息
            third_party_account.nickname = github_name
            third_party_account.avatar = github_avatar
            third_party_account.raw_profile = user_info

            # 获取关联的用户
            user = User.query.get(third_party_account.user_id)
            if user:
                user.ping()
                # 可选：更新用户信息
                if github_email and not user.email:
                    user.email = github_email

            else:
                logging.error(f"第三方账号关联的用户不存在: user_id={third_party_account.user_id}")
                return error(code=500, message="账号异常，请联系管理员")

        else:
            # 不存在：创建新用户和第三方账号记录
            # 生成唯一用户名
            base_username = f"gh_{github_login}"
            username = base_username
            counter = 1

            # 检查用户名是否重复，如重复则添加数字后缀
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1

            # 创建新用户
            user = User(
                username=username,
                nickname=github_name,
                email=github_email,
                image=github_avatar,
                location=github_location,
                about_me=github_bio,
                confirmed=True,  # 第三方登录用户默认已确认
            )

            db.session.add(user)
            db.session.flush()  # 刷新以获取 user.id

            # 创建第三方账号记录
            third_party_account = ThirdPartyAccount(
                provider="github",
                openid=github_id,
                unionid=None,  # GitHub 无 unionid
                nickname=github_name,
                avatar=github_avatar,
                raw_profile=user_info,
                user_id=user.id,
            )

            db.session.add(third_party_account)

        # 提交数据库事务
        db.session.commit()

        # 4. 生成 JWT token
        fresh_access_token = "Bearer " + create_access_token(identity=user, fresh=True)
        refresh_token = "Bearer " + create_refresh_token(identity=user)

        logging.info(f"GitHub 登录成功: user_id={user.id}, username={user.username}")

        return success(
            data=user.to_json(),
            access_token=fresh_access_token,
            refresh_token=refresh_token,
            message="登录成功",
        )

    except requests.exceptions.RequestException as e:
        logging.error(f"GitHub OAuth 网络请求失败: {str(e)}")
        return error(code=500, message="GitHub 登录失败，请稍后重试")
    except Exception as e:
        logging.error(f"GitHub OAuth 处理异常: {str(e)}", exc_info=True)
        return error(code=500, message="登录失败，请稍后重试")
