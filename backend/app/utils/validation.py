"""
数据校验工具函数
"""
from typing import Optional, Tuple, Type

from flask import Response, request
from pydantic import BaseModel, ValidationError

from .response import error


def validate_request_data(
    model_class: Type[BaseModel],
) -> Tuple[Optional[BaseModel], Optional[Response]]:
    """
    校验请求数据

    Args:
        model_class: Pydantic模型类

    Returns:
        Tuple[Optional[BaseModel], Optional[Response]]:
        - 如果校验成功，返回 (validated_data, None)
        - 如果校验失败，返回 (None, error_response)
    """
    try:
        # 获取JSON数据
        json_data = request.get_json()
        if json_data is None:
            return None, error(400, "请求数据格式错误")

        # 使用Pydantic模型校验数据
        validated_data = model_class(**json_data)
        return validated_data, None

    except ValidationError as e:
        # 提取第一个错误信息
        error_msg = e.errors()[0]["msg"]
        return None, error(400, error_msg)

    except Exception as e:
        return None, error(500, f"数据校验失败,{e}")


def validate_json_data(
    data: dict, model_class: Type[BaseModel]
) -> Tuple[Optional[BaseModel], Optional[str]]:
    """
    校验字典数据（用于测试和非Flask上下文）

    Args:
        data: 要校验的数据字典
        model_class: Pydantic模型类

    Returns:
        Tuple[Optional[BaseModel], Optional[str]]:
        - 如果校验成功，返回 (validated_data, None)
        - 如果校验失败，返回 (None, error_message)
    """
    try:
        validated_data = model_class(**data)
        return validated_data, None
    except ValidationError as e:
        error_msg = e.errors()[0]["msg"]
        return None, error_msg
    except Exception as e:
        return None, str(e)


def validate_data_with_response(
    data: dict, model_class: Type[BaseModel]
) -> Tuple[Optional[BaseModel], Optional[Response]]:
    """
    校验数据并返回Flask响应对象（用于API中）

    Args:
        data: 要校验的数据字典
        model_class: Pydantic模型类

    Returns:
        Tuple[Optional[BaseModel], Optional[Response]]:
        - 如果校验成功，返回 (validated_data, None)
        - 如果校验失败，返回 (None, error_response)
    """
    try:
        validated_data = model_class(**data)
        return validated_data, None
    except ValidationError as e:
        error_msg = e.errors()[0]["msg"]
        return None, error(400, error_msg)
    except Exception as e:
        return None, error(500, f"数据校验失败,{e}")


def validate_json(model_class: Type[BaseModel]):
    """
    装饰器：校验JSON请求数据

    Args:
        model_class: Pydantic模型类

    Returns:
        装饰器函数
    """
    from functools import wraps

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # 获取JSON数据
                json_data = request.get_json()
                if json_data is None:
                    return error(400, "请求数据格式错误")

                # 使用Pydantic模型校验数据
                validated_data = model_class(**json_data)

                # 将校验后的数据作为参数传递给原函数
                return f(validated_data, *args, **kwargs)

            except ValidationError as e:
                # 提取第一个错误信息
                error_msg = e.errors()[0]["msg"]
                return error(400, error_msg)

            except Exception as e:
                return error(500, f"数据校验失败,{e}")

        return decorated_function

    return decorator
