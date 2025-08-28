from flask import request
from flask_jwt_extended import jwt_required, decode_token
from flask_socketio import join_room, disconnect, ConnectionRefusedError
from . import socketio, db, logger
from .utils.socket_util import ManageSocket
from .utils.status import UserStatus
from .models import User, Message, Notification, NotificationType

# 获取日志记录器
log = logger.get_logger()
# 初始化状态管理器和WebSocket管理器
status_manager = UserStatus()
socket_manager = ManageSocket()


@socketio.on('connect')
@jwt_required(optional=True)
def handle_connect():
    try:
        user_id = verify_token_in_websocket()
        status_manager.init_user_status(user_id)
        record_user_connect(user_id)
        # 注意：join_room 已在 record_user_connect 中调用
        log.info(f"用户 {user_id} 已连接，Socket ID: {request.sid}")
    except Exception as e:
        log.error(f"WebSocket连接处理异常: {str(e)}", exc_info=True)
        raise


@socketio.on('disconnect')
@jwt_required(optional=True)
def handle_disconnect():
    try:
        user_id = verify_token_in_websocket()
        removed_user_id = socket_manager.remove_user_socket(request.sid)
        if removed_user_id:
            status_manager.del_user_status(user_id)
            log.info(f"用户 {user_id} 断开连接，Socket ID: {request.sid}")
        else:
            log.warning(f"断开连接处理: 未找到Socket ID {request.sid} 对应的用户")
    except Exception as e:
        log.error(f"WebSocket断开连接处理异常: {str(e)}", exc_info=True)


@socketio.on('heartbeat')
@jwt_required(optional=True)
def handle_heartbeat():
    user_id = verify_token_in_websocket()
    status_manager.update_last_active(user_id)


@socketio.on('enter_chat')
@jwt_required(optional=True)
def handle_enter_chat(data):
    user_id = verify_token_in_websocket()
    target_id = data['targetId']

    status_manager.active_chat(user_id, target_id)
    status_manager.update_last_active(user_id)
    status_manager.expire(60 * 5)

    # 标记已读并清除通知
    Message.query.filter(Message.receiver_id == user_id, Message.sender_id == target_id,
                         Message.is_read == False).update({'is_read': True}, synchronize_session='fetch')
    # 有问题 不应该删除。 应该标记为已读
    query = Notification.query.filter_by(receiver_id=user_id, trigger_user_id=target_id, type=NotificationType.CHAT,
                                         is_read=False).update({'is_read': True})
    # query = Notification.query.filter_by(receiver_id=user_id, trigger_user_id=target_id, type=NotificationType.CHAT).delete()
    print('query', query)
    db.session.commit()
    print(f'{user_id}进入聊天页{target_id}了')


@socketio.on('send_message')
@jwt_required(optional=True)
def handle_send_message(data):
    sender_id = verify_token_in_websocket()
    receiver_id = data['receiver_id']
    log.info(f'用户 {sender_id} 发送消息给用户 {receiver_id}')
    
    msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=data['content'])
    db.session.add(msg)
    db.session.flush()
    
    try:
        from .utils.socket_helper import safe_emit
        
        receiver_status = status_manager.get_user_status(receiver_id)
        if receiver_status and receiver_status.get('active_chat') == str(sender_id):
            log.debug(f'用户 {receiver_id} 当前正在与用户 {sender_id} 聊天')
            msg.is_read = True
            safe_emit('new_message', msg.to_json(), to=str(receiver_id))
        else:
            # 接收者离线或者不在聊天页面，都生成通知
            notification = Notification(receiver_id=receiver_id, trigger_user_id=sender_id, type=NotificationType.CHAT)
            db.session.add(notification)
            db.session.flush()
            
            if receiver_status is not None and receiver_status.get('online') == '1':
                log.debug(f'用户 {receiver_id} 在线但不在聊天页面')
                safe_emit('new_notification', notification.to_json(), to=str(receiver_id))
            else:
                log.debug(f'用户 {receiver_id} 离线，消息已保存，下次上线可查看通知')
        
        db.session.commit()
        safe_emit('message_sent', msg.to_json(), room=request.sid)
    except Exception as e:
        db.session.rollback()
        print('消息发送失败', str(e))


def verify_token_in_websocket():
    """连接websocket时验证用户身份"""
    try:
        token = request.args.get('token')
        if not token:
            # 尝试从请求头中获取token
            auth_header = request.headers.get('Authorization')
            if auth_header:
                token = auth_header.replace("Bearer ", "", 1)
            else:
                log.warning("WebSocket连接尝试没有提供token")
                raise ConnectionRefusedError('Unauthorized: 未提供认证令牌')
        
        raw_token = token.replace("Bearer ", "", 1)
        # 手动解码 Token
        decoded_token = decode_token(raw_token)
        user_id = decoded_token["sub"]
        
        # 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            log.warning(f"WebSocket连接尝试: 用户ID {user_id} 不存在")
            raise ConnectionRefusedError("websocket身份验证失败: 用户不存在")
        
        # 确保返回的是字符串类型的用户ID
        user_id_str = str(user_id)
        log.info(f"WebSocket连接验证成功: 用户ID {user_id_str} (原始类型: {type(user_id).__name__})")
        return user_id_str
    except Exception as e:
        log.error(f"WebSocket身份验证失败: {str(e)}", exc_info=True)
        raise ConnectionRefusedError("websocket身份验证失败: token解析错误")


def record_user_connect(user_id):
    """记录已连接的用户"""
    try:
        # 确保用户ID是字符串类型
        user_id_str = str(user_id)
        
        # 获取用户现有的连接
        old_sids = socket_manager.get_user_socket(user_id)
        log.info(f"用户 {user_id} 现有连接数: {len(old_sids)}")
        
        # 记录新连接
        socket_manager.add_user_socket(user_id, request.sid)
        
        # 将用户加入以其ID命名的房间
        join_room(user_id_str)
        log.info(f"用户 {user_id} 已加入房间 {user_id_str}")
        
        # 记录连接数量
        connection_count = socket_manager.get_connection_count(user_id)
        log.info(f"用户 {user_id} 现有 {connection_count} 个活跃连接")
        
        # 打印所有连接信息，用于调试
        socket_manager.debug_connections()
        
        # 定期清理可能存在的孤立连接
        orphaned = socket_manager.cleanup_orphaned_connections()
        if orphaned > 0:
            log.info(f"已清理 {orphaned} 个孤立连接")
    except Exception as e:
        log.error(f"记录用户连接时出错: {str(e)}", exc_info=True)
