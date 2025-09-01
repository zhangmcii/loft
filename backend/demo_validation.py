"""
Pydantic校验功能演示脚本
"""
from app.schemas.user_schemas import (
    RegisterRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    BindEmailRequest,
    ChangeEmailRequest
)
from app.utils.validation import validate_json_data


def demo_register_validation():
    """演示注册数据校验"""
    print("=== 注册数据校验演示 ===")
    
    # 合法数据
    valid_data = {
        "username": "testuser123",
        "password": "password123",
        "email": "test@example.com"
    }
    validated_data, error = validate_json_data(valid_data, RegisterRequest)
    print(f"合法数据校验结果: {validated_data is not None}, 错误: {error}")
    
    # 不合法数据 - 用户名过短
    invalid_data = {
        "username": "ab",
        "password": "password123",
        "email": "test@example.com"
    }
    validated_data, error = validate_json_data(invalid_data, RegisterRequest)
    print(f"用户名过短校验结果: {validated_data is not None}, 错误: {error}")
    
    # 不合法数据 - 密码无数字
    invalid_data2 = {
        "username": "testuser",
        "password": "password",
        "email": "test@example.com"
    }
    validated_data, error = validate_json_data(invalid_data2, RegisterRequest)
    print(f"密码无数字校验结果: {validated_data is not None}, 错误: {error}")


def demo_change_password_validation():
    """演示修改密码数据校验"""
    print("\n=== 修改密码数据校验演示 ===")
    
    # 合法数据
    valid_data = {
        "old_password": "oldpass123",
        "new_password": "newpass456"
    }
    validated_data, error = validate_json_data(valid_data, ChangePasswordRequest)
    print(f"合法数据校验结果: {validated_data is not None}, 错误: {error}")
    
    # 不合法数据 - 新密码无字母
    invalid_data = {
        "old_password": "oldpass123",
        "new_password": "123456"
    }
    validated_data, error = validate_json_data(invalid_data, ChangePasswordRequest)
    print(f"新密码无字母校验结果: {validated_data is not None}, 错误: {error}")


def demo_email_validation():
    """演示邮箱相关校验"""
    print("\n=== 邮箱相关校验演示 ===")
    
    # 绑定邮箱 - 合法数据
    valid_bind_data = {
        "email": "new@example.com",
        "code": "1234"
    }
    validated_data, error = validate_json_data(valid_bind_data, BindEmailRequest)
    print(f"绑定邮箱合法数据校验结果: {validated_data is not None}, 错误: {error}")
    
    # 绑定邮箱 - 验证码非数字
    invalid_bind_data = {
        "email": "new@example.com",
        "code": "abc4"
    }
    validated_data, error = validate_json_data(invalid_bind_data, BindEmailRequest)
    print(f"验证码非数字校验结果: {validated_data is not None}, 错误: {error}")


if __name__ == "__main__":
    demo_register_validation()
    demo_change_password_validation()
    demo_email_validation()
    print("\n演示完成！")