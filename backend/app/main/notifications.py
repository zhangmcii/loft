# 日志
import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required

from .. import db, socketio
from ..models import Follow, Notification, NotificationType
from ..utils.response import success
from . import main


# --------------------------- 通知功能 ---------------------------
def new_post_notification(post_id):
    """创建新文章通知并推送给粉丝"""
    # 查询当前用户的所有粉丝（排除自己）
    followers = Follow.query.filter_by(followed_id=current_user.id).all()

    # 为每个粉丝创建通知并推送
    for follow in followers:
        # 跳过作者自己（虽然逻辑上自己不会关注自己，但以防万一）
        if follow.follower_id == current_user.id:
            continue

        # 创建通知
        notification = Notification(
            receiver_id=follow.follower_id,  # 粉丝ID
            trigger_user_id=current_user.id,  # 触发用户（作者）
            post_id=post_id,  # 关联文章ID
            type=NotificationType.NewPost,  # 通知类型：新文章
        )
        db.session.add(notification)
        db.session.flush()  # 刷新以获取通知ID

        # 实时推送给粉丝
        socketio.emit(
            "new_notification",
            notification.to_json(),
            to=str(follow.follower_id),  # 发送到粉丝的房间
        )

    # 提交所有通知
    db.session.commit()


@main.route("/notifications")
@jwt_required()
def get_currentUsernotification():
    """获取当前用户的所有通知"""
    logging.info(f"获取用户通知: user_id={current_user.id}")
    # 预加载触发用户数据避免N+1查询
    from sqlalchemy.orm import joinedload
    from ..models import User

    notifications = (
        Notification.query.options(
            joinedload(Notification.trigger_user).load_only(
                User.id, User.username, User.nickname, User.image
            )
        )
        .filter_by(receiver_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return success(data=[item.to_json() for item in notifications])


@main.route("/notification/read", methods=["POST"])
@jwt_required()
def mark_read_notification():
    """标记通知为已读"""
    logging.info(f"标记通知已读: user_id={current_user.id}")
    ids = request.get_json().get("ids", [])
    Notification.query.filter(
        Notification.id.in_(ids), Notification.receiver_id == current_user.id
    ).update({"is_read": True}, synchronize_session=False)
    db.session.commit()
    return success(message="通知已标记为已读")
