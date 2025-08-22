"""
日志系统模块
"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import time


class Logger:
    def __init__(self, app=None):
        self.app = app
        self.logger = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化日志系统"""
        log_level = app.config.get('LOG_LEVEL', logging.INFO)
        log_dir = app.config.get('LOG_DIR', 'logs')
        log_name = app.config.get('LOG_NAME', 'flask_app')
        
        # 确保日志目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建日志记录器
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(log_level)
        
        # 清除已有的处理器
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '[ %(asctime)s - %(levelname)s - %(module)s - %(funcName)s ]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(formatter)
        # console_handler.setLevel(log_level)
        # self.logger.addHandler(console_handler)
        
        # 文件处理器（按天切割）
        log_file = os.path.join(log_dir, f"{log_name}.log")
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30,  # 保留30天的日志
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        self.logger.addHandler(file_handler)
        
        # 将日志记录器添加到应用上下文
        app.logger = self.logger
        
        self.logger.info(f"日志系统初始化完成，日志级别: {log_level}")
    
    def get_logger(self):
        """获取日志记录器"""
        if not self.logger:
            raise RuntimeError("日志系统尚未初始化，请先调用init_app方法")
        return self.logger


# 创建全局日志实例
logger = Logger()


def get_logger():
    """获取全局日志记录器"""
    return log