"""
用户API校验示例
展示如何在实际API中使用Pydantic校验模型
"""
from flask import Blueprint, request
from ..schemas.user_schemas import (
    RegisterRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    BindEmailRequest,
    ChangeEmailRequest
)
from ..utils.validation import validate_json
from ..utils.response import success, error

# 创建蓝图
user_validation_bp = Blueprint('user_validation', __name__, url_prefix='/api/user')


@user_validation_bp.route('/register', methods=['POST'])
@validate_json(RegisterRequest)
def register(validated_data: RegisterRequest):
    """
    用户注册接口
    
    Args:
        validated_data: 经过校验的注册数据
    
    Returns:
        统一响应格式
    """
    try:
        # 这里是实际的业务逻辑
        # 1. 检查用户名是否已存在
        # 2. 检查邮箱是否已被使用
        # 3. 验证验证码
        # 4. 创建用户账号
        
        # 示例：模拟注册成功
        user_data = {
            'username': validated_data.username,
            'email': validated_data.email,
            'created_at': '2024-01-01 00:00:00'
        }
        
        return success(data=user_data, message="注册成功")
        
    except Exception as e:
        return error(500, f"注册失败: {str(e)}")


@user_validation_bp.route('/change-password', methods=['POST'])
@validate_json(ChangePasswordRequest)
def change_password(validated_data: ChangePasswordRequest):
    """
    修改密码接口
    
    Args:
        validated_data: 经过校验的修改密码数据
    
    Returns:
        统一响应格式
    """
    try:
        # 这里是实际的业务逻辑
        # 1. 验证原密码是否正确
        # 2. 更新用户密码
        # 3. 可能需要使所有session失效
        
        return success(message="密码修改成功")
        
    except Exception as e:
        return error(500, f"密码修改失败: {str(e)}")


@user_validation_bp.route('/forgot-password', methods=['POST'])
@validate_json(ForgotPasswordRequest)
def forgot_password(validated_data: ForgotPasswordRequest):
    """
    忘记密码接口
    
    Args:
        validated_data: 经过校验的忘记密码数据
    
    Returns:
        统一响应格式
    """
    try:
        # 这里是实际的业务逻辑
        # 1. 验证邮箱是否存在
        # 2. 验证验证码是否正确
        # 3. 重置用户密码
        
        return success(message="密码重置成功")
        
    except Exception as e:
        return error(500, f"密码重置失败: {str(e)}")


@user_validation_bp.route('/bind-email', methods=['POST'])
@validate_json(BindEmailRequest)
def bind_email(validated_data: BindEmailRequest):
    """
    绑定邮箱接口
    
    Args:
        validated_data: 经过校验的绑定邮箱数据
    
    Returns:
        统一响应格式
    """
    try:
        # 这里是实际的业务逻辑
        # 1. 验证验证码是否正确
        # 2. 检查邮箱是否已被其他用户使用
        # 3. 如果需要密码验证，验证当前密码
        # 4. 绑定邮箱到当前用户
        
        return success(message="邮箱绑定成功")
        
    except Exception as e:
        return error(500, f"邮箱绑定失败: {str(e)}")


@user_validation_bp.route('/change-email', methods=['POST'])
@validate_json(ChangeEmailRequest)
def change_email(validated_data: ChangeEmailRequest):
    """
    修改邮箱接口
    
    Args:
        validated_data: 经过校验的修改邮箱数据
    
    Returns:
        统一响应格式
    """
    try:
        # 这里是实际的业务逻辑
        # 1. 验证原邮箱是否为当前用户的邮箱
        # 2. 验证验证码是否正确
        # 3. 检查新邮箱是否已被其他用户使用
        # 4. 如果需要密码验证，验证当前密码
        # 5. 更新用户邮箱
        
        return success(message="邮箱修改成功")
        
    except Exception as e:
        return error(500, f"邮箱修改失败: {str(e)}")