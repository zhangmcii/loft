"""
第三方登录统一处理模块
基于 senweaver-oauth 实现可扩展的第三方登录系统
"""
import logging
import os
from typing import Dict, List, Optional

from flask import current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from senweaver_oauth import AuthConfig
from senweaver_oauth.builder import AuthRequestBuilder
from senweaver_oauth.enums.auth_source import AuthDefaultSource

from .. import db
from ..models import ThirdPartyAccount, User
from ..utils.response import error, success

logger = logging.getLogger(__name__)


# OAuth 配置字典，支持多平台扩展
OAUTH_CONFIGS = {
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GITHUB_REDIRECT_URI", ""),
    },
    "gitee": {
        "client_id": os.getenv("GITEE_CLIENT_ID", ""),
        "client_secret": os.getenv("GITEE_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GITEE_REDIRECT_URI", ""),
    },
    "qq": {
        "client_id": os.getenv("QQ_CLIENT_ID", ""),
        "client_secret": os.getenv("QQ_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("QQ_REDIRECT_URI", ""),
    },
    "wechat": {
        "client_id": os.getenv("WECHAT_CLIENT_ID", ""),
        "client_secret": os.getenv("WECHAT_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("WECHAT_REDIRECT_URI", ""),
    },
    "wechat_open": {
        "client_id": os.getenv("WECHAT_OPEN_CLIENT_ID", ""),
        "client_secret": os.getenv("WECHAT_OPEN_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("WECHAT_OPEN_REDIRECT_URI", ""),
    },
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", ""),
    },
    "weibo": {
        "client_id": os.getenv("WEIBO_CLIENT_ID", ""),
        "client_secret": os.getenv("WEIBO_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("WEIBO_REDIRECT_URI", ""),
    },
    "dingtalk": {
        "client_id": os.getenv("DINGTALK_CLIENT_ID", ""),
        "client_secret": os.getenv("DINGTALK_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("DINGTALK_REDIRECT_URI", ""),
    },
    "facebook": {
        "client_id": os.getenv("FACEBOOK_CLIENT_ID", ""),
        "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("FACEBOOK_REDIRECT_URI", ""),
    },
    "baidu": {
        "client_id": os.getenv("BAIDU_CLIENT_ID", ""),
        "client_secret": os.getenv("BAIDU_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("BAIDU_REDIRECT_URI", ""),
    },
    "feishu": {
        "client_id": os.getenv("FEISHU_CLIENT_ID", ""),
        "client_secret": os.getenv("FEISHU_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("FEISHU_REDIRECT_URI", ""),
    },
    "linkedin": {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID", ""),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI", ""),
    },
    "microsoft": {
        "client_id": os.getenv("MICROSOFT_CLIENT_ID", ""),
        "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("MICROSOFT_REDIRECT_URI", ""),
    },
    "douyin": {
        "client_id": os.getenv("DOUYIN_CLIENT_ID", ""),
        "client_secret": os.getenv("DOUYIN_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("DOUYIN_REDIRECT_URI", ""),
    },
    "twitter": {
        "client_id": os.getenv("TWITTER_CLIENT_ID", ""),
        "client_secret": os.getenv("TWITTER_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("TWITTER_REDIRECT_URI", ""),
    },
}


def get_available_providers() -> List[Dict]:
    """
    获取已配置的 OAuth 提供商列表
    返回格式: [{"provider": "github", "name": "GitHub", "enabled": True}]
    """
    result = []
    for provider, config in OAUTH_CONFIGS.items():
        if config["client_id"] and config["client_secret"]:
            source = AuthDefaultSource.get_source(provider)
            if source is None:
                source = AuthDefaultSource.GITHUB  # 默认为 GitHub
            result.append(
                {
                    "provider": provider,
                    "name": source.name
                    if hasattr(source, "name")
                    else provider.capitalize(),
                    "enabled": True,
                }
            )
    return result


def get_oauth_config(provider: str) -> Optional[Dict]:
    """获取指定 provider 的 OAuth 配置"""
    config = OAUTH_CONFIGS.get(provider)
    if not config or not config.get("client_id") or not config.get("client_secret"):
        return None
    return config


def create_or_update_user(auth_user_data, provider: str) -> User:
    """
    创建或更新用户及第三方账号绑定

    Args:
        auth_user_data: senweaver-oauth 返回的用户数据对象
        provider: 第三方平台标识

    Returns:
        User: 用户对象
    """
    # 提取第三方账号信息
    openid = getattr(auth_user_data, "uuid", "") or auth_user_data.uuid
    unionid = getattr(auth_user_data, "unionid", None)
    nickname = getattr(auth_user_data, "nickname", "") or getattr(
        auth_user_data, "username", ""
    )
    avatar = getattr(auth_user_data, "avatar", "")
    raw_profile = {
        "uuid": getattr(auth_user_data, "uuid", ""),
        "username": getattr(auth_user_data, "username", ""),
        "nickname": getattr(auth_user_data, "nickname", ""),
        "avatar": avatar,
        "email": getattr(auth_user_data, "email", ""),
        "gender": getattr(auth_user_data, "gender", ""),
        "source": getattr(auth_user_data, "source", ""),
    }

    # 查询是否已绑定该第三方账号
    third_party = ThirdPartyAccount.query.filter_by(
        provider=provider, openid=openid
    ).first()

    if third_party:
        # 更新第三方账号快照信息
        third_party.nickname = nickname
        third_party.avatar = avatar
        third_party.unionid = unionid
        third_party.raw_profile = raw_profile

        # 获取用户并更新基本信息
        user = User.query.get(third_party.user_id)
        if user:
            if not user.nickname and nickname:
                user.nickname = nickname
            if not user.image and avatar:
                user.image = avatar

        logger.info(f"第三方账号已存在，更新用户: {user.username if user else 'unknown'}")
        return user

    # 创建新用户
    username = f"{provider}_{openid[:8]}"  # 生成唯一用户名
    # 确保用户名唯一
    counter = 1
    original_username = username
    while User.query.filter_by(username=username).first():
        username = f"{original_username}_{counter}"
        counter += 1

    user = User(
        username=username,
        nickname=nickname,
        image=avatar,
        confirmed=True,  # 第三方登录用户默认已认证
    )
    db.session.add(user)
    db.session.flush()  # 获取 user.id

    # 创建第三方账号绑定
    third_party = ThirdPartyAccount(
        provider=provider,
        openid=openid,
        unionid=unionid,
        nickname=nickname,
        avatar=avatar,
        raw_profile=raw_profile,
        user_id=user.id,
    )
    db.session.add(third_party)
    db.session.commit()

    logger.info(f"创建新用户: {username} 绑定第三方账号: {provider}")
    return user


def handle_oauth_callback(provider: str, callback_params: Dict):
    """
    处理 OAuth 回调

    Args:
        provider: 第三方平台标识
        callback_params: 回调参数字典

    Returns:
        tuple: (success: bool, data: dict, error_message: str)
    """
    config = get_oauth_config(provider)
    if not config:
        return False, None, f"平台 {provider} 未正确配置"

    try:
        # 创建 OAuth 配置
        auth_config = AuthConfig(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config["redirect_uri"],
        )

        # 构建认证请求并处理回调
        auth_request = (
            AuthRequestBuilder.builder()
            .source(provider)
            .auth_config(auth_config)
            .build()
        )

        logger.info(f"处理 {provider} OAuth 回调: {callback_params}")

        # 调用登录方法获取用户信息
        auth_response = auth_request.login(callback_params)

        # 检查响应状态
        if auth_response.code != 200 or not auth_response.data:
            error_msg = auth_response.message or "获取用户信息失败"
            logger.error(f"{provider} OAuth 登录失败: {error_msg}")
            return False, None, error_msg

        # 检查是否有服务 URL 跳转
        if auth_response.data.service_url:
            logger.info(f"需要跳转到服务页面: {auth_response.data.service_url}")
            return False, None, f"需要跳转: {auth_response.data.service_url}"

        # 创建或更新用户
        user = create_or_update_user(auth_response.data, provider)

        # 生成 JWT tokens
        access_token = "Bearer " + create_access_token(identity=user, fresh=True)
        refresh_token = "Bearer " + create_refresh_token(identity=user)

        logger.info(f"用户 {user.username} 通过 {provider} 登录成功")

        return (
            True,
            {
                "user": user.to_json(),
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            None,
        )

    except Exception as e:
        logger.error(f"处理 {provider} OAuth 回调异常: {str(e)}", exc_info=True)
        return False, None, str(e)


def get_oauth_providers():
    """获取可用的 OAuth 提供商列表接口"""
    providers = get_available_providers()
    return success(data=providers)


def oauth_login(provider: str):
    """
    OAuth 登录接口 - 重定向到第三方授权页面

    Query 参数:
        redirect_url: 登录成功后前端希望跳转的 URL（可选）
    """
    config = get_oauth_config(provider)
    if not config:
        return error(code=404, message=f"未支持的平台: {provider}")

    try:
        auth_config = AuthConfig(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config["redirect_uri"],
        )

        # 构建授权请求
        auth_request = (
            AuthRequestBuilder.builder()
            .source(provider)
            .auth_config(auth_config)
            .build()
        )

        auth_url = auth_request.authorize()

        # 重定向到第三方授权页面
        return redirect(auth_url)

    except Exception as e:
        logger.error(f"创建 {provider} 授权请求失败: {str(e)}")
        return error(code=500, message=f"创建授权请求失败: {str(e)}")


def oauth_callback(provider: str):
    """
    OAuth 回调接口 - 处理第三方授权回调，返回 JSON
    """
    # 获取回调参数
    callback_params = dict(request.args)

    # 处理 OAuth 回调
    success_flag, data, error_msg = handle_oauth_callback(provider, callback_params)

    if not success_flag:
        # 登录失败，返回错误信息
        return error(code=400, message=error_msg)

    # 登录成功，返回 tokens 和用户信息
    return success(data=data)


def oauth_callback_api(provider: str):
    """
    OAuth 回调 API 接口 - 用于前端回调页面调用
    将所有 URL 参数传递给后端处理
    """
    # 获取所有回调参数
    callback_params = dict(request.args)

    # 处理 OAuth 回调
    success_flag, data, error_msg = handle_oauth_callback(provider, callback_params)

    if not success_flag:
        # 登录失败，返回错误信息
        return error(code=400, message=error_msg)

    # 登录成功，返回 tokens 和用户信息
    return success(data=data)
