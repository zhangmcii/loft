"""
数据校验工具函数
"""
from functools import wraps
from flask import request
from pydantic import BaseModel, ValidationError
from ..utils.response import error


def validate_json(schema_class: BaseModel):
    """
    JSON数据校验装饰器
    
    Args:
        schema_class: Pydantic模型类
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 获取JSON数据
                json_data = request.get_json()
                if not json_data:
                    return error(400, "请求数据不能为空")
                
                # 使用Pydantic模型校验数据
                validated_data = schema_class(**json_data)
                
                # 将校验后的数据传递给视图函数
                return func(validated_data, *args, **kwargs)
                
            except ValidationError as e:
                # 提取第一个错误信息
                error_msg = e.errors()[0]['msg']
                field_name = e.errors()[0]['loc'][0] if e.errors()[0]['loc'] else '未知字段'
                return error(400, f"{field_name}: {error_msg}")
            except ValueError as e:
                return error(400, str(e))
            except Exception as e:
                return error(500, f"数据校验失败: {str(e)}")
        
        return wrapper
    return decorator


def validate_form(schema_class: BaseModel):
    """
    表单数据校验装饰器
    
    Args:
        schema_class: Pydantic模型类
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 获取表单数据
                form_data = request.form.to_dict()
                if not form_data:
                    return error(400, "请求数据不能为空")
                
                # 使用Pydantic模型校验数据
                validated_data = schema_class(**form_data)
                
                # 将校验后的数据传递给视图函数
                return func(validated_data, *args, **kwargs)
                
            except ValidationError as e:
                # 提取第一个错误信息
                error_msg = e.errors()[0]['msg']
                field_name = e.errors()[0]['loc'][0] if e.errors()[0]['loc'] else '未知字段'
                return error(400, f"{field_name}: {error_msg}")
            except ValueError as e:
                return error(400, str(e))
            except Exception as e:
                return error(500, f"数据校验失败: {str(e)}")
        
        return wrapper
    return decorator