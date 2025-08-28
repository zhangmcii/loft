from .decorators import DecoratedMethodView
from flask_jwt_extended import jwt_required
from . import api
from ..models import Log, User
from ..decorators import admin_required
from .. import db
from flask import request, current_app
from ..utils.response import success, error
from .. import logger

# 日志
log = logger.get_logger()


# --------------------------- 日志管理 ---------------------------
@api.route("/online-users")
@admin_required
@jwt_required()
def online():
    """获取在线用户信息"""
    log.info("获取在线用户信息")
    from ..utils.socket_util import ManageSocket

    manage_socket = ManageSocket()
    # 在线人数信息
    user_ids = manage_socket.user_socket.keys()
    users = []
    for user_id in user_ids:
        u = User.query.get(user_id)
        users.append({"username": u.username, "nickName": u.nickname})
    online_total = len(users)
    return success(data=users, extra={"total": online_total})


class LogApi(DecoratedMethodView):
    method_decorators = {
        'share': [jwt_required(), admin_required],
    }

    def get(self):
        """获取系统日志"""
        log.info("获取系统日志")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["FLASKY_LOG_PER_PAGE"], type=int
        )
        query = Log.query
        paginate = query.order_by(Log.operate_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        logs = paginate.items
        return success(data=[log.to_json() for log in logs], extra={"total": query.count()})

    def post(self):
        """删除系统日志"""
        log.info("删除系统日志")
        try:
            ids = request.get_json().get("ids", [])
            if not ids:
                return success(message="没有提供要删除的日志ID")
            Log.query.filter(Log.id.in_(ids)).delete()
            db.session.commit()
            return success(message="日志删除成功")
        except Exception as e:
            log.error(f"删除日志失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"删除日志失败: {str(e)}")


def register_log_api(bp, *, logs_url):
    _log = LogApi.as_view('logs')
    bp.add_url_rule(logs_url, view_func=_log)
