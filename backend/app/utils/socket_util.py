#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from threading import Lock
import time


# 管理WebSocket连接
class ManageSocket:
    """
    WebSocket连接管理器，使用单例模式确保全局唯一实例
    负责跟踪用户与socket连接的映射关系
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            logging.info("创建WebSocket管理器实例")
        return cls._instance

    def __init__(self):
        # 只在首次初始化时设置属性
        if not hasattr(self, 'initialized'):
            logging.info("初始化WebSocket管理器")
            self.user_socket = {}  # { user_id: set(sid_1, sid_2) }
            self.socket_user = {}  # { socket_id: user_id }
            self.lock = Lock()
            self.last_cleanup = time.time()
            self.initialized = True

    def add_user_socket(self, user_id, sid):
        """
        添加用户与socket连接的映射关系
        
        Args:
            user_id: 用户ID
            sid: Socket连接ID
        """
        with self.lock:
            try:
                # 清理已存在的映射
                if sid in self.socket_user:
                    old_user = self.socket_user[sid]
                    if old_user in self.user_socket:
                        self.user_socket[old_user].discard(sid)
                        logging.info(f"移除旧映射: 用户 {old_user} 的连接 {sid}")
                        if not self.user_socket[old_user]:
                            del self.user_socket[old_user]
                            logging.info(f"用户 {old_user} 没有活跃连接，移除记录")
                
                # 添加新映射
                if user_id not in self.user_socket:
                    self.user_socket[user_id] = set()
                    logging.info(f"为用户 {user_id} 创建新的连接集合")
                
                self.user_socket[user_id].add(sid)
                self.socket_user[sid] = user_id
                logging.info(f"用户 {user_id} 建立新连接 {sid}，当前连接数: {len(self.user_socket[user_id])}")
            except Exception as e:
                logging.error(f"添加用户连接映射时出错: {str(e)}", exc_info=True)

    def get_user_socket(self, user_id):
        """
        获取用户的所有socket连接ID
        
        Args:
            user_id: 用户ID
            
        Returns:
            set: 用户的socket连接ID集合
        """
        with self.lock:
            try:
                # 返回副本避免线程安全问题
                sockets = self.user_socket.get(user_id, set()).copy()
                logging.info(f"获取用户 {user_id} 的连接，共 {len(sockets)} 个")
                return sockets
            except Exception as e:
                logging.error(f"获取用户连接时出错: {str(e)}", exc_info=True)
                return set()

    def remove_user_socket(self, sid):
        """
        移除socket连接的映射关系
        
        Args:
            sid: Socket连接ID
        """
        with self.lock:
            try:
                if sid in self.socket_user:
                    user_id = self.socket_user[sid]
                    if user_id in self.user_socket:
                        self.user_socket[user_id].discard(sid)
                        logging.info(f"移除用户 {user_id} 的连接 {sid}")
                        if not self.user_socket[user_id]:
                            del self.user_socket[user_id]
                            logging.info(f"用户 {user_id} 已断开所有连接")
                    del self.socket_user[sid]
                    return user_id
                return None
            except Exception as e:
                logging.error(f"移除用户连接时出错: {str(e)}", exc_info=True)
                return None
    
    def get_online_users_count(self):
        """
        获取当前在线用户数量
        
        Returns:
            int: 在线用户数量
        """
        with self.lock:
            count = len(self.user_socket)
            logging.info(f"当前在线用户数: {count}")
            return count
    
    def cleanup_stale_connections(self):
        """
        清理可能的过期连接（定期维护用）
        """
        current_time = time.time()
        # 每10分钟执行一次清理
        if current_time - self.last_cleanup < 600:
            return
            
        with self.lock:
            try:
                before_count = len(self.socket_user)
                # 实际清理逻辑可根据需要实现
                # 这里只是记录日志，表明执行了清理
                logging.info(f"执行连接清理，清理前连接数: {before_count}")
                self.last_cleanup = current_time
            except Exception as e:
                logging.error(f"清理过期连接时出错: {str(e)}", exc_info=True)
