from flask_jwt_extended import jwt_required
from . import main
from ..models import Log
from ..decorators import admin_required
from .. import db
from flask import request, current_app
from ..utils.response import success, error


# 日志
import logging


# --------------------------- 日志管理 ---------------------------
@main.route("/logs", methods=["GET"])
@admin_required
@jwt_required()
def logs():
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
    return success(data=[logging.to_json() for log in logs], total=query.count())


@main.route("/deleteLog", methods=["POST"])
@admin_required
@jwt_required()
def delete_log():
    """删除系统日志"""
    logging.info("删除系统日志")
    try:
        ids = request.get_json().get("ids", [])
        if not ids:
            return success(message="没有提供要删除的日志ID")
        Log.query.filter(Log.id.in_(ids)).delete()
        db.session.commit()
        return success(message="日志删除成功")
    except Exception as e:
        logging.error(f"删除日志失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"删除日志失败: {str(e)}")