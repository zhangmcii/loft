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
