#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers
from datetime import datetime

def setup_logging(app=None):
    """
    配置全局日志系统，使用根记录器
    
    Args:
        app: Flask应用实例，可选
    """
    # 获取根记录器
    root_logger = logging.getLogger()
    
    # 如果已经配置过处理器，则不重复配置
    if root_logger.handlers:
        return
    
    # 设置日志级别
    root_logger.setLevel(logging.DEBUG)
    
    # 创建日志目录
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs'))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志文件路径
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 创建文件处理器
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=30, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # 设置格式化器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到根记录器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 如果提供了Flask应用，则配置Flask日志
    if app:
        # 将Flask的日志处理器替换为我们的处理器
        for handler in app.logger.handlers:
            app.logger.removeHandler(handler)
        
        # 设置Flask日志级别
        app.logger.setLevel(logging.DEBUG)
        
        # 将Flask日志传递给父记录器
        app.logger.propagate = True
        
    logging.info("日志系统初始化完成")

# 在模块导入时自动进行基本配置，确保在任何地方导入logging都能使用
# 这样可以保证在应用启动前就能使用日志功能
setup_logging()