import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from .. import db
from ..decorators import DecoratedMethodView
from ..models import Notification
from ..utils.response import success


# --------------------------- 通知功能 ---------------------------
class NotificationApi(DecoratedMethodView):
    method_decorators = {
        "share": [jwt_required()],
    }

    def get(self):
        """获取当前用户的所有通知"""
        logging.info(f"获取用户通知: user_id={current_user.id}")
        d = (
            Notification.query.filter_by(receiver_id=current_user.id)
            .order_by(Notification.created_at.desc())
            .all()
        )
        return success(data=[item.to_json() for item in d])

    def patch(self):
        """标记通知为已读"""
        logging.info(f"标记通知已读: user_id={current_user.id}")
        ids = request.get_json().get("ids", [])
        Notification.query.filter(
            Notification.id.in_(ids), Notification.receiver_id == current_user.id
        ).update({"is_read": True}, synchronize_session=False)
        db.session.commit()
        return success(message="通知已标记为已读")


def register_notification_api(bp, *, notification_url):
    bp.add_url_rule(
        f"/{notification_url}", view_func=NotificationApi.as_view("notification")
    )
