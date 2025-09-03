import os
from functools import wraps

import requests
from flask import abort, request
from flask_jwt_extended import current_user
from user_agents import parse

from . import db
from .models import Log, Permission
from .utils.time_util import DateUtils

from flask import request
from flask.views import MethodView


class DecoratedMethodView(MethodView):
    method_decorators = {
        # '方法名': [装饰器列表]
        # 'get': [admin_required],
        # 'post': [user_required],
        # 共有的
        # 'share': [],
    }

    def dispatch_request(self, *args, **kwargs):
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == "HEAD":
            meth = getattr(self, "get", None)
        assert meth is not None, f"Unimplemented method {request.method}"
        share = self.method_decorators.get("share", [])
        # 逐个装饰当前方法
        for dec in share + self.method_decorators.get(request.method.lower(), []):
            meth = dec(meth)
        return meth(*args, **kwargs)


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


def log_operate(f):
    def decorate(*args, **kwargs):
        if request.args.get("page", 1, type=int) != 1:
            return f(*args, **kwargs)

        # 用户身份信息
        is_register = True if current_user else False
        client_info = get_client_info()
        client_info.update(
            {
                "username": current_user.username if is_register else "游客",
                "operate": "访问首页",
            }
        )

        # 构建查询条件
        log_filter = {"username": client_info.get("username")}
        if not is_register:
            log_filter = {"ip": client_info.get("ip")}

        # 获取最近访问记录
        last_visit = (
            Log.query.filter_by(**log_filter).order_by(Log.operate_time.desc()).first()
        )

        # 判断访问间隔
        now = DateUtils.now_time()
        should_log = not last_visit or DateUtils.datetime_diff(
            now, DateUtils.datetime_to_str(last_visit.operate_time), 5
        )

        # 记录日志
        if should_log:
            db.session.add(Log(**client_info))
            db.session.commit()
        return f(*args, **kwargs)

    return decorate


def get_client_info():
    if "X-Forwarded-For" in request.headers:
        client_ip = request.headers.get("X-Forwarded-For")
    else:
        client_ip = request.remote_addr

    # 获取用户地理位置
    if os.environ.get("FLASK_DEBUG", None):
        country = None
        city = None
    else:
        try:
            r = requests.get(f"https://ipapi.co/{client_ip}/json/")
            local_data = r.json()
            country = local_data.get("country_name")
            city = local_data.get("city")
        except Exception:
            country = None
            city = None

    # 获取设备信息
    user_agent = request.headers.get("user-agent")
    ua = parse(user_agent)
    user_info = {
        "browser": ua.browser.family,
        "browser_version": ua.browser.version_string,
        "os": ua.os.family,
        "os_version": ua.os.version_string,
        "device": ua.device.family,
        "ip": client_ip,
        "country": country,
        "city": city,
    }
    if os.environ.get("FLASK_DEBUG", None):
        pass
        # print('44', user_info)
    return user_info
