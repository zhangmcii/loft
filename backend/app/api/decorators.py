from functools import wraps
from .errors import forbidden
from flask_jwt_extended import current_user
from flask.views import MethodView
from flask import request


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)

        return decorated_function

    return decorator


class DecoratedMethodView(MethodView):
    method_decorators = {
        # '方法名': [装饰器列表]
        # 'get': [admin_required],
        # 'post': [user_required],

        # 公共的
        # 'share': [],
    }



    def dispatch_request(self, *args, **kwargs):
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == "HEAD":
            meth = getattr(self, "get", None)
        assert meth is not None, f"Unimplemented method {request.method}"
        share = self.method_decorators.get('share', [])
        # 逐个装饰当前方法
        for dec in share+ self.method_decorators.get(request.method.lower(), []):
            meth = dec(meth)
        return meth(*args, **kwargs)
