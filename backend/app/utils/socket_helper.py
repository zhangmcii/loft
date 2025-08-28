"""
WebSocket 辅助函数模块
提供安全的 WebSocket 消息发送功能
"""
import logging
from .. import socketio
from .socket_util import ManageSocket

# 获取日志记录器
logger = logging.getLogger('websocket')
socket_manager = ManageSocket()

def safe_emit(event, data, to=None, room=None, namespace=None):
    """
    安全地发送 WebSocket 消息
    
    参数:
    - event: 事件名称
    - data: 要发送的数据
    - to: 目标用户ID (可选)
    - room: 目标房间 (可选)
    - namespace: 命名空间 (可选)
    
    返回:
    - bool: 是否成功发送
    """
    try:
        if to is not None:
            # 确保用户ID是字符串类型
            user_id_str = str(to)
            
            # 打印所有连接信息，用于调试
            socket_manager.debug_connections()
            
            # 检查用户是否有活跃连接
            user_sockets = socket_manager.get_user_socket(user_id_str)
            if not user_sockets:
                logger.warning(f"用户 {to} (转换为 {user_id_str}) 没有活跃连接，消息未发送: {event}")
                
                # 尝试使用原始ID再次查找
                if str(to) != to:
                    user_sockets = socket_manager.get_user_socket(to)
                    if user_sockets:
                        logger.info(f"使用原始ID {to} 找到了用户连接，数量: {len(user_sockets)}")
                        user_id_str = to
                    else:
                        return False
                else:
                    return False
            
            # 记录详细日志
            logger.info(f"尝试发送 '{event}' 消息给用户 {to}，当前连接数: {len(user_sockets)}")
            
            # 发送到用户的房间
            try:
                # 同时尝试发送到用户ID和用户ID字符串对应的房间
                socketio.emit(event, data, to=user_id_str, namespace=namespace)
                logger.info(f"消息 '{event}' 已发送给用户 {to} (房间: {user_id_str})")
                
                # 记录消息内容
                if data:
                    logger.debug(f"消息内容: {str(data)[:100]}...")
                
                return True
            except Exception as e:
                logger.error(f"发送消息 '{event}' 给用户 {to} 时出错: {str(e)}")
                return False
        elif room is not None:
            # 发送到指定房间
            socketio.emit(event, data, room=room, namespace=namespace)
            logger.debug(f"消息 '{event}' 已发送到房间 {room}")
            return True
        else:
            # 广播消息
            socketio.emit(event, data, namespace=namespace)
            logger.debug(f"消息 '{event}' 已广播")
            return True
    except Exception as e:
        logger.error(f"发送WebSocket消息失败: {str(e)}", exc_info=True)
        return False

def send_notification(user_id, notification_data):
    """
    发送通知给指定用户
    
    参数:
    - user_id: 目标用户ID
    - notification_data: 通知数据
    
    返回:
    - bool: 是否成功发送
    """
    return safe_emit("new_notification", notification_data, to=user_id)

def send_message(user_id, message_data):
    """
    发送消息给指定用户
    
    参数:
    - user_id: 目标用户ID
    - message_data: 消息数据
    
    返回:
    - bool: 是否成功发送
    """
    return safe_emit("new_message", message_data, to=user_id)

def broadcast_event(event, data):
    """
    广播事件给所有连接的用户
    
    参数:
    - event: 事件名称
    - data: 事件数据
    
    返回:
    - bool: 是否成功广播
    """
    return safe_emit(event, data)