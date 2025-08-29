import logging
from flask import request
from flask_jwt_extended import jwt_required, decode_token
from flask_socketio import join_room, disconnect, ConnectionRefusedError
from . import socketio, db
from .utils.socket_util import ManageSocket
from .utils.status import UserStatus
from .models import User, Message, Notification, NotificationType

status_manager = UserStatus()
socket_manager = ManageSocket()


@socketio.on('connect')
@jwt_required(optional=True)
def handle_connect():
    user_id = verify_token_in_websocket()
    status_manager.init_user_status(user_id)
    record_user_connect(user_id)
    join_room(str(user_id))
    logging.info(f"用户 {user_id} 已连接，新连接ID：{request.sid}")


@socketio.on('disconnect')
@jwt_required(optional=True)
def handle_disconnect():
    user_id = verify_token_in_websocket()
    socket_manager.remove_user_socket(request.sid)
    status_manager.del_user_status(user_id)
    logging.info(f"用户 {user_id} 已断开连接，状态：{status_manager.get_user_status(user_id)}")


@socketio.on('heartbeat')
@jwt_required(optional=True)
def handle_heartbeat():
    user_id = verify_token_in_websocket()
    status_manager.update_last_active(user_id)
    logging.debug(f"用户 {user_id} 发送心跳包")


@socketio.on('enter_chat')
@jwt_required(optional=True)
def handle_enter_chat(data):
    user_id = verify_token_in_websocket()
    target_id = data['targetId']

    status_manager.active_chat(user_id, target_id)
    status_manager.update_last_active(user_id)
    status_manager.expire(60 * 5)
    
    logging.info(f"用户 {user_id} 进入与用户 {target_id} 的聊天页面")

    try:
        # 标记已读并清除通知
        updated_messages = Message.query.filter(
            Message.receiver_id == user_id, 
            Message.sender_id == target_id,
            Message.is_read == False
        ).update({'is_read': True}, synchronize_session='fetch')
        
        logging.debug(f"已将 {updated_messages} 条消息标记为已读")
        
        # 标记通知为已读
        updated_notifications = Notification.query.filter_by(
            receiver_id=user_id, 
            trigger_user_id=target_id, 
            type=NotificationType.CHAT,
            is_read=False
        ).update({'is_read': True})
        
        logging.debug(f"已将 {updated_notifications} 条通知标记为已读")
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"更新消息和通知状态失败: {str(e)}", exc_info=True)


@socketio.on('send_message')
@jwt_required(optional=True)
def handle_send_message(data):
    sender_id = verify_token_in_websocket()
    receiver_id = data['receiver_id']
    content = data['content']
    logging.info(f"用户 {sender_id} 发送消息给用户 {receiver_id}: {content[:20]}...")
    
    msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.session.add(msg)
    db.session.flush()
    
    try:
        receiver_status = status_manager.get_user_status(receiver_id)
        logging.debug(f"接收者 {receiver_id} 状态: {receiver_status}")
        
        if receiver_status and receiver_status.get('active_chat') == str(sender_id):
            logging.info(f"用户 {receiver_id} 当前正在与发送者 {sender_id} 聊天")
            msg.is_read = True
            socketio.emit('new_message', msg.to_json(), to=str(receiver_id))
        else:
            # 接收者离线或者不在聊天页面，都生成通知
            notification = Notification(receiver_id=receiver_id, trigger_user_id=sender_id, type=NotificationType.CHAT)
            db.session.add(notification)
            db.session.flush()
            
            if receiver_status is not None and receiver_status.get('online') == '1':
                logging.info(f"用户 {receiver_id} 在线但不在聊天页面，发送通知")
                socketio.emit('new_notification', notification.to_json(), to=str(receiver_id))
            else:
                logging.info(f"用户 {receiver_id} 离线，消息已保存，下次上线可查看通知")
                
        db.session.commit()
        socketio.emit('message_sent', msg.to_json(), room=request.sid)
        logging.debug(f"消息 ID:{msg.id} 发送成功")
    except Exception as e:
        db.session.rollback()
        logging.error(f"消息发送失败: {str(e)}", exc_info=True)


def verify_token_in_websocket():
    """连接websocket时验证用户身份"""
    try:
        token = request.args.get('token')
        if not token:
            logging.warning("WebSocket连接缺少token")
            raise ConnectionRefusedError('未授权：缺少token')
            
        raw_token = token.replace("Bearer ", "", 1)
        # 手动解码 Token
        decoded_token = decode_token(raw_token)
        user_id = decoded_token["sub"]
        logging.debug(f"WebSocket连接token验证成功，用户ID: {user_id}")
    except Exception as e:
        logging.error(f"WebSocket身份验证失败: {str(e)}", exc_info=True)
        raise ConnectionRefusedError("WebSocket身份验证失败，token解析错误")
        
    # 检查用户是否存在
    user = User.query.get(user_id)
    if not user:
        logging.warning(f"WebSocket连接失败: 用户ID {user_id} 不存在")
        raise ConnectionRefusedError("WebSocket身份验证失败，用户不存在")
        
    return user.username


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
