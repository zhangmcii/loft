from threading import Lock
import logging

# 获取日志记录器
logger = logging.getLogger('websocket')

# 管理socket连接
class ManageSocket:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.user_socket = {}  # { user_id: set(sid_1, sid_2) }
            self.socket_user = {}  # { socket_id: user_id }
            self.lock = Lock()
            self.initialized = True
            logger.info("WebSocket管理器初始化完成")
            
    def debug_connections(self):
        """
        打印当前所有连接信息，用于调试
        """
        with self.lock:
            logger.info(f"===== WebSocket连接调试信息 =====")
            logger.info(f"总连接数: {len(self.socket_user)}")
            logger.info(f"总用户数: {len(self.user_socket)}")
            
            for user_id, sockets in self.user_socket.items():
                logger.info(f"用户 {user_id} (类型: {type(user_id)}) 有 {len(sockets)} 个连接: {sockets}")
            
            logger.info(f"===== 调试信息结束 =====")

    def add_user_socket(self, user_id, sid):
        """
        添加用户的WebSocket连接
        :param user_id: 用户ID
        :param sid: Socket ID
        """
        with self.lock:
            # 确保用户ID是字符串类型
            user_id = str(user_id)
            
            # 清理已存在的映射
            if sid in self.socket_user:
                old_user_id = self.socket_user[sid]  # 修复：使用正确的键名
                logger.debug(f"Socket {sid} 已存在映射到用户 {old_user_id}，正在清理")
                
                if old_user_id in self.user_socket:
                    self.user_socket[old_user_id].discard(sid)
                    
                    if not self.user_socket[old_user_id]:
                        del self.user_socket[old_user_id]
                        logger.debug(f"用户 {old_user_id} 没有活跃连接，已移除")
            
            # 添加新映射
            if user_id not in self.user_socket:
                self.user_socket[user_id] = set()
                logger.debug(f"为用户 {user_id} 创建新的连接集合")
                
            self.user_socket[user_id].add(sid)
            self.socket_user[sid] = user_id
            logger.info(f"用户 {user_id} 添加新连接 {sid}，当前连接数: {len(self.user_socket[user_id])}")

    def get_user_socket(self, user_id):
        """
        获取用户的所有WebSocket连接
        :param user_id: 用户ID
        :return: 该用户的所有Socket ID集合的副本
        """
        with self.lock:
            # 确保用户ID是字符串类型
            user_id_str = str(user_id)
            
            # 首先尝试使用字符串类型的用户ID
            sockets = self.user_socket.get(user_id_str, set()).copy()
            
            # 如果找不到，尝试使用原始类型的用户ID
            if not sockets and user_id != user_id_str:
                sockets = self.user_socket.get(user_id, set()).copy()
                
                # 如果找到了，将其迁移到字符串键
                if sockets:
                    logger.info(f"将用户 {user_id} 的连接从原始键迁移到字符串键 {user_id_str}")
                    self.user_socket[user_id_str] = sockets.copy()
                    del self.user_socket[user_id]
                    
                    # 更新 socket_user 映射
                    for sid in sockets:
                        self.socket_user[sid] = user_id_str
            
            logger.info(f"获取用户 {user_id_str} 的连接，数量: {len(sockets)}")
            return sockets

    def remove_user_socket(self, sid):
        """
        移除指定的WebSocket连接
        :param sid: Socket ID
        """
        with self.lock:
            if sid in self.socket_user:
                user_id = self.socket_user[sid]
                logger.debug(f"正在移除Socket {sid} (用户 {user_id})")
                
                if user_id in self.user_socket:
                    self.user_socket[user_id].discard(sid)
                    logger.debug(f"从用户 {user_id} 的连接集合中移除 {sid}")
                    
                    if not self.user_socket[user_id]:
                        del self.user_socket[user_id]
                        logger.info(f"用户 {user_id} 没有活跃连接，已从映射中移除")
                
                del self.socket_user[sid]
                logger.debug(f"Socket {sid} 已从映射中移除")
                return user_id
            else:
                logger.warning(f"尝试移除不存在的Socket连接: {sid}")
                return None

    def get_all_connected_users(self):
        """
        获取所有已连接的用户ID
        :return: 用户ID列表
        """
        with self.lock:
            return list(self.user_socket.keys())

    def get_connection_count(self, user_id=None):
        """
        获取连接数量
        :param user_id: 可选，指定用户ID
        :return: 连接数量
        """
        with self.lock:
            if user_id:
                return len(self.user_socket.get(user_id, set()))
            else:
                return len(self.socket_user)

    def cleanup_orphaned_connections(self):
        """
        清理孤立的连接（socket_user中存在但user_socket中不存在的连接）
        """
        with self.lock:
            orphaned_sids = []
            for sid, user_id in list(self.socket_user.items()):
                if user_id not in self.user_socket or sid not in self.user_socket[user_id]:
                    orphaned_sids.append(sid)
            
            for sid in orphaned_sids:
                del self.socket_user[sid]
                logger.warning(f"清理孤立的Socket连接: {sid}")
            
            if orphaned_sids:
                logger.info(f"共清理了 {len(orphaned_sids)} 个孤立的Socket连接")
            
            return len(orphaned_sids)