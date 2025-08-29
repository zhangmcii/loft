#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class LoggerCompat:
    """
    兼容层，用于支持旧的logger.get_logger()调用方式
    """
    @staticmethod
    def get_logger():
        """
        获取根日志记录器
        
        Returns:
            logging.Logger: 根日志记录器
        """
        return logging.getLogger()

# 创建全局兼容实例
logger = LoggerCompat()

def get_logger():
    """获取全局日志记录器"""
    return logging.getLogger()