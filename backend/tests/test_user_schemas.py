"""
用户数据校验模型的单元测试
"""
import pytest
from app.schemas.user_schemas import (
    RegisterRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    BindEmailRequest,
    ChangeEmailRequest
)
from app.utils.validation import validate_json_data


class TestRegisterRequest:
    """注册请求校验测试"""
    
    def test_valid_register_data(self):
        """测试合法的注册数据"""
        valid_data = {
            "username": "testuser123",
            "password": "password123",
            "email": "test@example.com"
        }
        validated_data, error = validate_json_data(valid_data, RegisterRequest)
        assert validated_data is not None
        assert error is None
        assert validated_data.username == "testuser123"
    
    def test_invalid_username_too_short(self):
        """测试用户名过短"""
        invalid_data = {
            "username": "ab",
            "password": "password123",
            "email": "test@example.com"
        }
        validated_data, error = validate_json_data(invalid_data, RegisterRequest)
        assert validated_data is None
        assert "at least 3 characters" in error
    
    def test_invalid_username_special_chars(self):
        """测试用户名包含特殊字符"""
        invalid_data = {
            "username": "test@user",
            "password": "password123",
            "email": "test@example.com"
        }
        validated_data, error = validate_json_data(invalid_data, RegisterRequest)
        assert validated_data is None
        assert "用户名只能包含字母、数字和下划线" in error
    
    def test_invalid_password_no_letter(self):
        """测试密码不包含字母"""
        invalid_data = {
            "username": "testuser",
            "password": "123456",
            "email": "test@example.com"
        }
        validated_data, error = validate_json_data(invalid_data, RegisterRequest)
        assert validated_data is None
        assert "密码必须包含至少一个字母" in error
    
    def test_invalid_email_format(self):
        """测试邮箱格式错误"""
        invalid_data = {
            "username": "testuser",
            "password": "password123",
            "email": "invalid-email"
        }
        validated_data, error = validate_json_data(invalid_data, RegisterRequest)
        assert validated_data is None
        assert "value is not a valid email address" in error


class TestChangePasswordRequest:
    """修改密码请求校验测试"""
    
    def test_valid_change_password_data(self):
        """测试合法的修改密码数据"""
        valid_data = {
            "old_password": "oldpass123",
            "new_password": "newpass456"
        }
        validated_data, error = validate_json_data(valid_data, ChangePasswordRequest)
        assert validated_data is not None
        assert error is None
    
    def test_invalid_new_password_no_digit(self):
        """测试新密码不包含数字"""
        invalid_data = {
            "old_password": "oldpass123",
            "new_password": "newpassword"
        }
        validated_data, error = validate_json_data(invalid_data, ChangePasswordRequest)
        assert validated_data is None
        assert "新密码必须包含至少一个数字" in error


class TestForgotPasswordRequest:
    """忘记密码请求校验测试"""
    
    def test_valid_forgot_password_data(self):
        """测试合法的忘记密码数据"""
        valid_data = {
            "email": "test@example.com",
            "new_password": "newpass123",
            "code": "1234"
        }
        validated_data, error = validate_json_data(valid_data, ForgotPasswordRequest)
        assert validated_data is not None
        assert error is None
    
    def test_invalid_code_not_digit(self):
        """测试验证码不是数字"""
        invalid_data = {
            "email": "test@example.com",
            "new_password": "newpass123",
            "code": "abc4"
        }
        validated_data, error = validate_json_data(invalid_data, ForgotPasswordRequest)
        assert validated_data is None
        assert "验证码必须为数字" in error


class TestBindEmailRequest:
    """绑定邮箱请求校验测试"""
    
    def test_valid_bind_email_data(self):
        """测试合法的绑定邮箱数据"""
        valid_data = {
            "email": "new@example.com",
            "code": "5678"
        }
        validated_data, error = validate_json_data(valid_data, BindEmailRequest)
        assert validated_data is not None
        assert error is None
    
    def test_invalid_email_format(self):
        """测试邮箱格式错误"""
        invalid_data = {
            "email": "invalid.email",
            "code": "5678"
        }
        validated_data, error = validate_json_data(invalid_data, BindEmailRequest)
        assert validated_data is None
        assert "value is not a valid email address" in error


class TestChangeEmailRequest:
    """修改邮箱请求校验测试"""
    
    def test_valid_change_email_data(self):
        """测试合法的修改邮箱数据"""
        valid_data = {
            "new_email": "newemail@example.com",
            "code": "9999"
        }
        validated_data, error = validate_json_data(valid_data, ChangeEmailRequest)
        assert validated_data is not None
        assert error is None
    
    def test_invalid_code_too_short(self):
        """测试验证码过短"""
        invalid_data = {
            "new_email": "newemail@example.com",
            "code": "123"
        }
        validated_data, error = validate_json_data(invalid_data, ChangeEmailRequest)
        assert validated_data is None
        assert "at least 4 characters" in error