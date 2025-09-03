from flask_jwt_extended import jwt_required, current_user
from . import main
from ..models import Message
from .. import db
from flask import request, current_app
from ..utils.response import success


# 日志
import logging


# --------------------------- 聊天消息 ---------------------------
@main.route("/msg", methods=["GET"])
@jwt_required()
def get_message_history():
    """获取聊天历史记录"""
    logging.info(f"获取聊天历史: user_id={current_user.id}")
    current_user_id = current_user.id
    other_user_id = request.args.get("userId")
    page = request.args.get("page", 1, type=int)
    query = Message.query.filter(
        (
            (Message.sender_id == current_user_id)
            & (Message.receiver_id == other_user_id)
        )
        | (
            (Message.sender_id == other_user_id)
            & (Message.receiver_id == current_user_id)
        )
    ).order_by(Message.timestamp.desc())
    pagination = query.paginate(
        page=page, per_page=current_app.config["FLASKY_CHAT_PER_PAGE"], error_out=False
    )
    messages = pagination.items
    r = []
    _id = len(messages)
    for message in messages:
        r1 = message.to_json()
        r1.update({"id": _id})
        r.append(r1)
        _id -= 1
    return success(data=r, total=pagination.total)


@main.route("/msg/read", methods=["POST"])
@jwt_required()
def mark_messages_read():
    """标记消息为已读"""
    logging.info(f"标记消息已读: user_id={current_user.id}")
    message_ids = request.json.get("ids", [])
    Message.query.filter(
        Message.id.in_(message_ids), Message.receiver_id == current_user.id
    ).update({"is_read": True}, synchronize_session=False)
    db.session.commit()
    return success(message="消息已标记为已读")