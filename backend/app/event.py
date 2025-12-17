import logging
import eventlet
from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import ConnectionRefusedError, disconnect, join_room

from . import db
from .models import Message, Notification, NotificationType, User
from .utils.socket_util import ManageSocket
from .utils.status import UserStatus
from .mycelery.notification_task import create_chat_notifications

status_manager = UserStatus()
socket_manager = ManageSocket()


# 封装为注册函数
def register_ws_events(socketio, app):
    """注册WS事件，绑定传入的socketio实例和app上下文"""

    def verify_token_in_websocket():
        """连接websocket时验证用户身份"""
        try:
            token = request.args.get("token")
            if not token:
                logging.warning("WebSocket连接缺少token")
                raise ConnectionRefusedError("未授权：缺少token")

            raw_token = token.replace("Bearer ", "", 1)
            decoded_token = decode_token(raw_token)
            user_id = decoded_token["sub"]
            logging.info(f"WebSocket连接token验证成功，用户ID: {user_id}")
        except Exception as e:
            logging.error(f"WebSocket身份验证失败: {str(e)}", exc_info=True)
            raise ConnectionRefusedError("WebSocket身份验证失败，token解析错误")

        # 检查用户是否存在（DB操作，后续异步场景需绑定上下文）
        user = User.query.get(user_id)
        if not user:
            logging.warning(f"WebSocket连接失败: 用户ID {user_id} 不存在")
            raise ConnectionRefusedError("WebSocket身份验证失败，用户不存在")

        return user.username, user.id

    def record_user_connect(user_id):
        """记录已连接的用户"""
        try:
            old_sids = socket_manager.user_socket.get(user_id, set())
            if old_sids:
                logging.info(f"用户 {user_id} 有 {len(old_sids)} 个旧连接，将断开它们")

            for sid in list(old_sids):
                disconnect(sid)
                socket_manager.remove_user_socket(sid)

            # 记录新连接
            socket_manager.add_user_socket(user_id, request.sid)
            logging.info(f"用户 {user_id} 的新连接 {request.sid} 已记录")
        except Exception as e:
            logging.error(f"记录用户连接时出错: {str(e)}", exc_info=True)

    # 连接事件
    @socketio.on("connect")
    def handle_connect():
        username, user_id = verify_token_in_websocket()
        # 内存操作同步执行（无阻塞）
        status_manager.init_user_status(user_id)
        record_user_connect(user_id)
        join_room(str(user_id))
        logging.info(f"用户 {username} 已连接，新连接ID：{request.sid}")

    # 断开事件：纯内存操作，同步执行
    @socketio.on("disconnect")
    def handle_disconnect():
        username, user_id = verify_token_in_websocket()
        socket_manager.remove_user_socket(request.sid)
        status_manager.del_user_status(user_id)
        logging.info(
            f"用户 {username} 已断开连接，状态：{status_manager.get_user_status(user_id)}"
        )

    # 心跳事件：纯内存操作，同步执行
    @socketio.on("heartbeat")
    def handle_heartbeat():
        username, user_id = verify_token_in_websocket()
        status_manager.update_last_active(user_id)
        logging.info(f"用户 {username} 发送心跳包")

    # 进入聊天事件-异步DB操作（标记已读）
    def async_enter_chat(user_id, target_id):
        """异步处理进入聊天的DB操作（标记已读）"""
        with app.app_context():  # 绑定WS应用上下文
            try:
                # 标记消息已读
                updated_messages = Message.query.filter(
                    Message.receiver_id == user_id,
                    Message.sender_id == target_id,
                    Message.is_read.is_(False),
                ).update({"is_read": True}, synchronize_session="fetch")
                logging.info(f"已将 {updated_messages} 条消息标记为已读")

                # 标记通知已读
                updated_notifications = (
                    Notification.query.filter_by(
                        receiver_id=user_id,
                        trigger_user_id=target_id,
                        type=NotificationType.CHAT,
                    )
                    .filter(Notification.is_read.is_(False))
                    .update({"is_read": True})
                )
                logging.info(f"已将 {updated_notifications} 条通知标记为已读")

                db.session.commit()
            except Exception as e:
                db.session.rollback()  # 事务回滚
                logging.error(f"更新消息和通知状态失败: {str(e)}", exc_info=True)

    @socketio.on("enter_chat")
    def handle_enter_chat(data):
        username, user_id = verify_token_in_websocket()
        target_id = data["targetId"]

        # 内存操作同步执行
        status_manager.active_chat(user_id, target_id)
        status_manager.update_last_active(user_id)
        status_manager.expire(60 * 5)
        logging.info(f"用户 {username} 进入与用户 {target_id} 的聊天页面")

        # DB操作异步执行
        eventlet.spawn_n(async_enter_chat, user_id, target_id)

    # 发送消息事件-异步DB操作（消息入库+通知）
    def async_send_message(sender_id, receiver_id, content, sid):
        """异步处理发送消息的DB操作"""
        with app.app_context():
            msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
            db.session.add(msg)
            db.session.flush()

            try:
                receiver_status = status_manager.get_user_status(receiver_id)
                logging.info(f"接收者 {receiver_id} 状态: {receiver_status}")

                if receiver_status and receiver_status.get("active_chat") == str(
                    sender_id
                ):
                    logging.info(f"用户 {receiver_id} 当前正在与发送者 {sender_id} 聊天")
                    msg.is_read = True
                    socketio.emit("new_message", msg.to_json(), to=str(receiver_id))
                else:
                    # 异步生成通知（Celery任务）
                    create_chat_notifications.delay(receiver_id, sender_id, msg.id)
                    if receiver_status and receiver_status.get("online") == "1":
                        logging.info(f"用户 {receiver_id} 在线但不在聊天页面，消息已保存")
                    else:
                        logging.info(f"用户 {receiver_id} 离线，消息已保存")

                db.session.commit()
                socketio.emit("message_sent", msg.to_json(), room=sid)
                logging.info(f"消息 ID:{msg.id} 发送成功")
            except Exception as e:
                db.session.rollback()  # 事务回滚
                logging.error(f"消息发送失败: {str(e)}", exc_info=True)

    @socketio.on("send_message")
    def handle_send_message(data):
        username, sender_id = verify_token_in_websocket()
        receiver_id = data["receiver_id"]
        content = data["content"]
        logging.info(f"用户 {username} 发送消息给用户 {receiver_id}: {content[:20]}...")

        # DB操作异步执行
        eventlet.spawn_n(
            async_send_message, sender_id, receiver_id, content, request.sid
        )
