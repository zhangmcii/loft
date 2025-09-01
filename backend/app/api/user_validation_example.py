"""
用户API校验使用示例
展示如何在Flask路由中使用Pydantic校验模型
"""
from flask import Blueprint, request
from app.schemas.user_schemas import (
    RegisterRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    BindEmailRequest,
    ChangeEmailRequest
)
from app.utils.validation import validate_request_data
from app.utils.response import success, error

# 创建蓝图
user_validation_bp = Blueprint('user_validation', __name__, url_prefix='/api/user')


@user_validation_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口示例"""
    # 使用Pydantic校验请求数据
    validated_data, error_response = validate_request_data(RegisterRequest)
    if error_response:
        return error_response
    
    # 校验通过，处理业务逻辑
    username = validated_data.username
    password = validated_data.password
    email = validated_data.email
    
    # 这里添加实际的注册逻辑
    # user_service.create_user(username, password, email)
    
    return success({
        "username": username,
        "email": email
    }, "注册成功")


@user_validation_bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码接口示例"""
    validated_data, error_response = validate_request_data(ChangePasswordRequest)
    if error_response:
        return error_response
    
    old_password = validated_data.old_password
    new_password = validated_data.new_password
    
    # 这里添加实际的修改密码逻辑
    # user_service.change_password(current_user_id, old_password, new_password)
    
    return success(message="密码修改成功")


@user_validation_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """忘记密码接口示例"""
    validated_data, error_response = validate_request_data(ForgotPasswordRequest)
    if error_response:
        return error_response
    
    email = validated_data.email
    new_password = validated_data.new_password
    code = validated_data.code
    
    # 这里添加实际的重置密码逻辑
    # user_service.reset_password(email, new_password, code)
    
    return success(message="密码重置成功")


@user_validation_bp.route('/bind-email', methods=['POST'])
def bind_email():
    """绑定邮箱接口示例"""
    validated_data, error_response = validate_request_data(BindEmailRequest)
    if error_response:
        return error_response
    
    email = validated_data.email
    code = validated_data.code
    
    # 这里添加实际的绑定邮箱逻辑
    # user_service.bind_email(current_user_id, email, code)
    
    return success({"email": email}, "邮箱绑定成功")


@user_validation_bp.route('/change-email', methods=['POST'])
def change_email():
    """修改邮箱接口示例"""
    validated_data, error_response = validate_request_data(ChangeEmailRequest)
    if error_response:
        return error_response
    
    new_email = validated_data.new_email
    code = validated_data.code
    
    # 这里添加实际的修改邮箱逻辑
    # user_service.change_email(current_user_id, new_email, code)
    
    return success({"new_email": new_email}, "邮箱修改成功")