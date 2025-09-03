import logging

from flask import current_app, request
from flask_jwt_extended import jwt_required

from .. import db
from ..decorators import admin_required
from ..models import Log, User
from ..utils.response import error, success
from ..utils.socket_util import ManageSocket
from . import api
from .decorators import DecoratedMethodView


# --------------------------- 日志管理 ---------------------------
@api.route("/online-users")
@admin_required
@jwt_required()
def online():
    """获取在线用户信息"""
    logging.info("获取在线用户信息")

    manage_socket = ManageSocket()
    # 在线人数信息
    user_ids = manage_socket.user_socket.keys()
    logging.info(f"在线用户:{user_ids}")
    online_users = User.query.filter(User.id.in_(user_ids))
    users = []
    for u in online_users:
        users.append({"username": u.username, "nickName": u.nickname})
    return success(data=users, total=manage_socket.get_online_users_count())


class LogApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required(), admin_required],
    }

    def get(self):
        """获取系统日志"""
        logging.info("获取系统日志")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["FLASKY_LOG_PER_PAGE"], type=int
        )
        query = Log.query
        paginate = query.order_by(Log.operate_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        logs = paginate.items
        logging.info(f"获取到 {len(logs)} 条日志记录")
        return success(data=[logging.to_json() for log in logs], total=query.count())

    def post(self):
        """删除系统日志"""
        logging.info("删除系统日志")
        try:
            ids = request.get_json().get("ids", [])
            if not ids:
                logging.info("没有提供要删除的日志ID")
                return success(message="没有提供要删除的日志ID")

            deleted_count = Log.query.filter(Log.id.in_(ids)).delete()
            db.session.commit()
            logging.info(f"成功删除 {deleted_count} 条日志记录")
            return success(message=f"成功删除 {deleted_count} 条日志记录")
        except Exception as e:
            logging.error(f"删除日志失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"删除日志失败: {str(e)}")


def register_log_api(bp, *, logs_url):
    logging.info(f"注册日志API: {logs_url}")
    _log = LogApi.as_view("logs")
    bp.add_url_rule(logs_url, view_func=_log)
