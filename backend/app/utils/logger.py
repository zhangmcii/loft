#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers
from logging.handlers import SMTPHandler
from datetime import datetime

def setup_logging(app=None):
    """
    配置全局日志系统，使用根记录器
    
    Args:
        app: Flask应用实例，可选
    """
     # 获取根记录器
    root_logger = logging.getLogger()
    
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
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 只在没有处理器时添加，避免重复添加
    if not root_logger.handlers:
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    logging.info("基本日志系统初始化完成")
    

    # 如果提供了Flask应用，则配置Flask日志
    if app:
        # 移除原有处理器
        for handler in list(app.logger.handlers):
            app.logger.removeHandler(handler)
        # 添加新的处理器
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.propagate = True

        # 邮件处理器
        if not app.debug:
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_DEFAULT_SENDER'],
                toaddrs=['1912592745@qq.com'],
                subject='Flask App Error',
                credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
                secure=() if app.config.get("MAIL_USE_TLS") else None
            )
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(formatter)
            root_logger.addHandler(mail_handler)
            logging.info(f"已配置邮件处理器")
            logging.info("应用日志系统初始化完成")


# 在模块导入时自动进行基本配置，确保在任何地方导入logging都能使用
# 这样可以保证在应用启动前就能使用日志功能
setup_logging()