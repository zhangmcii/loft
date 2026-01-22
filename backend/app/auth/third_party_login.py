from __future__ import annotations

import json
import logging
import os
import re
import secrets
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode

from flask import redirect, request, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from senweaver_oauth import AuthConfig
from senweaver_oauth.builder import AuthRequestBuilder

from .. import db
from ..models import ThirdPartyAccount, User
from ..utils.response import error, success
from . import auth

# 第三方授权平台
APP_NAMES = ["qq", "weibo", "github", "google"]


# 平台配置：仅在存在 client_id & client_secret 时才会启用
def _read_config(app_names: list[str]) -> Dict[str, Dict]:
    result = {}
    for name in app_names:
        pre_fix = name.upper()
        result[name] = {
            "display_name": name,
            "client_id": os.getenv(f"{pre_fix}_CLIENT_ID", ""),
            "client_secret": os.getenv(f"{pre_fix}_CLIENT_SECRET", ""),
            # 可为空，后端自动生成
            "redirect_uri": os.getenv(f"{pre_fix}_REDIRECT_URI"),
        }
    return result


OAUTH_CONFIGS = _read_config(APP_NAMES)


# 回跳到前端的页面（例如 https://your-frontend.com/oauth/callback）
_host = os.getenv("FLASK_RUN_HOST")
_port = "80" if os.getenv("FLASK_CONFIG") == "docker" else "5172"

FRONTEND_OAUTH_REDIRECT = f"http://{_host}:{_port}/oauth/callback"


def _enabled_providers() -> List[str]:
    """过滤掉未配置的平台"""
    return [
        name
        for name, cfg in OAUTH_CONFIGS.items()
        if cfg.get("client_id") and cfg.get("client_secret")
    ]


def _get_auth_request(provider: str) -> Tuple[AuthRequestBuilder, Dict]:
    """
    构建 senweaver-oauth 的统一授权请求实例。
    """
    config = OAUTH_CONFIGS.get(provider)
    if not config:
        raise ValueError(f"未支持的平台: {provider}")
    if not config.get("client_id") or not config.get("client_secret"):
        raise ValueError(f"平台 {provider} 未正确配置")

    # 若未显式配置 redirect_uri，则自动使用当前域名生成
    redirect_uri = config.get("redirect_uri") or url_for(
        "auth.oauth_callback", provider=provider, _external=True
    )

    auth_config = AuthConfig(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        redirect_uri=redirect_uri,
        extras=config.get("extras", {}),
    )

    # senweaver-oauth 在内部会对传入的字符串执行 upper()
    # 因此这里统一传字符串，避免直接传 AuthSource 对象导致缺少 upper 方法
    source_name = config.get("source") or provider

    auth_request = (
        AuthRequestBuilder.builder()
        .source(source_name)
        .auth_config(auth_config)
        .build()
    )

    return auth_request, {"redirect_uri": redirect_uri}


def _safe_profile(raw_profile) -> Optional[Dict]:
    """确保 raw_profile 可序列化为 JSON"""
    if raw_profile is None:
        return None
    try:
        return json.loads(json.dumps(raw_profile, default=str))
    except Exception as exc:  # noqa: BLE001
        logging.warning("原始第三方资料序列化失败: %s", exc)
        return None


def _generate_username(base_name: str) -> str:
    """
    基于第三方昵称生成唯一用户名。
    """
    slug = re.sub(r"[^a-zA-Z0-9_]+", "", base_name or "").lower() or "user"
    candidate = slug
    index = 1
    while User.query.filter_by(username=candidate).first():
        candidate = f"{slug}{index}"
        index += 1
    return candidate


def _get_or_create_user(provider: str, auth_user) -> User:
    """将第三方账号落地到 User + ThirdPartyAccount"""
    # provider = auth_user.source (已在调用方传入 provider)
    uuid = getattr(auth_user, "uuid", None)
    if not uuid:
        raise ValueError("第三方登录缺少 uuid")

    # 从 AuthUser 标准字段提取用户信息
    username = auth_user.username
    nickname = auth_user.nickname
    avatar = getattr(auth_user, "avatar", None)
    email = getattr(auth_user, "email", None)
    mobile = getattr(auth_user, "mobile", None)
    gender = auth_user.gender.value if auth_user.gender else None
    location = getattr(auth_user, "location", None)
    company = getattr(auth_user, "company", None)
    blog = getattr(auth_user, "blog", None)
    remark = getattr(auth_user, "remark", None)
    raw_user_info = _safe_profile(getattr(auth_user, "raw_user_info", None))

    account = ThirdPartyAccount.query.filter_by(
        provider=provider, uuid=uuid
    ).one_or_none()

    if account:
        # 已绑定用户，更新快照信息
        account.nickname = nickname
        account.avatar = avatar
        account.email = email
        account.mobile = mobile
        account.gender = gender
        account.location = location
        account.company = company
        account.blog = blog
        account.remark = remark
        account.raw_user_info = raw_user_info
        db.session.add(account)
        user = User.query.get(account.user_id)
        if user and (not user.image and avatar):
            user.image = avatar
            db.session.add(user)
        return user

    # 创建用户
    username = _generate_username(username)
    user = User(
        username=username,
        nickname=nickname,
        image=avatar,
        # 生成不可预测的密码，防止密码登录
        password=secrets.token_urlsafe(32),
    )
    db.session.add(user)
    # 获取 user.id
    db.session.flush()

    account = ThirdPartyAccount(
        provider=provider,
        uuid=uuid,
        username=username,
        nickname=nickname,
        avatar=avatar,
        email=email,
        mobile=mobile,
        gender=gender,
        location=location,
        company=company,
        blog=blog,
        remark=remark,
        raw_user_info=raw_user_info,
        user_id=user.id,
    )
    db.session.add(account)
    return user


@auth.route("/oauth/providers", methods=["GET"])
def list_oauth_providers():
    """
    返回已启用的平台列表，前端据此动态渲染按钮。
    """
    providers = []
    for provider in _enabled_providers():
        providers.append(
            {
                "provider": provider,
                "name": OAUTH_CONFIGS[provider].get("display_name", provider.title()),
                "authorize_endpoint": url_for(
                    "auth.oauth_authorize", provider=provider, _external=False
                ),
            }
        )
    return success(data={"providers": providers})


@auth.route("/oauth/authorize/<provider>", methods=["GET"])
def oauth_authorize(provider: str):
    """
    返回第三方授权地址（由前端跳转）。
    """
    try:
        auth_request, _ = _get_auth_request(provider)
        auth_url = auth_request.authorize()
        return success(data={"authorize_url": auth_url, "provider": provider})
    except Exception as exc:  # noqa: BLE001
        logging.exception("创建授权请求失败: %s", exc)
        return error(code=400, message=str(exc))


@auth.route("/oauth/callback/<provider>", methods=["GET"])
def oauth_callback(provider: str):
    """
    第三方回调：
    - 统一解析第三方用户
    - 落库（User / ThirdPartyAccount）
    - 签发 JWT，并跳转到前端处理页面
    """
    params = dict(request.args)
    try:
        auth_request, meta = _get_auth_request(provider)
        logging.info(
            "处理第三方回调 provider=%s redirect_uri=%s params=%s",
            provider,
            meta["redirect_uri"],
            params,
        )

        auth_user_response = auth_request.login(params)
        if auth_user_response.code != 200 or not auth_user_response.data:
            return error(
                code=auth_user_response.code or 400,
                message=auth_user_response.message or "第三方登录失败",
            )

        auth_user = auth_user_response.data
        if getattr(auth_user, "service_url", None):
            # 个别平台需要前往服务页面
            return redirect(auth_user.service_url)

        user = _get_or_create_user(provider, auth_user)
        db.session.commit()

        # 登录态

        user_payload = user.to_json()
        access_token = "Bearer " + create_access_token(identity=user, fresh=True)
        refresh_token = "Bearer " + create_refresh_token(identity=user)

        # 更新最近活跃
        user.ping()

        # 返回给前端
        if FRONTEND_OAUTH_REDIRECT:
            query = urlencode(
                {
                    "provider": provider,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": json.dumps(user_payload),
                }
            )
            return redirect(f"{FRONTEND_OAUTH_REDIRECT}?{query}")

        return success(
            data=user_payload,
            access_token=access_token,
            refresh_token=refresh_token,
            message="登录成功",
        )
    except Exception as exc:  # noqa: BLE001
        logging.exception("处理第三方登录失败: %s", exc)
        db.session.rollback()
        return error(code=500, message="处理第三方登录失败")
