"""
数据校验模型单元测试
"""
import pytest
from pydantic import ValidationError
from app.schemas.user_schemas import (
    RegisterRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    BindEmailRequest,
    ChangeEmailRequest
)


class TestRegisterRequest:
    """注册请求模型测试"""
    
    def test_valid_register_data(self):
        """测试合法的注册数据"""
        valid_data = {
            "username": "testuser123",
            "password": "password123",
            "confirm_password": "password123",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        request = RegisterRequest(**valid_data)
        assert request.username == "testuser123"
        assert request.password == "password123"
        # assert request.email == "test@example.com"
        # assert request.verification_code == "123456"
    
    def test_valid_chinese_username(self):
        """测试中文用户名"""
        valid_data = {
            "username": "测试用户123",
            "password": "password123",
            "confirm_password": "password123",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        request = RegisterRequest(**valid_data)
        assert request.username == "测试用户123"
    
    def test_username_too_short(self):
        """测试用户名过短"""
        invalid_data = {
            "username": "ab",
            "password": "password123",
            "confirm_password": "password123",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(error['msg']) for error in errors)
    
    def test_username_too_long(self):
        """测试用户名过长"""
        invalid_data = {
            "username": "a" * 21,
            "password": "password123",
            "confirm_password": "password123",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("at most 20 characters" in str(error['msg']) for error in errors)
    
    def test_invalid_username_characters(self):
        """测试用户名包含非法字符"""
        invalid_data = {
            "username": "test@user",
            "password": "password123",
            "confirm_password": "password123",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("只能包含字母、数字、下划线和中文字符" in str(error['msg']) for error in errors)
    
    def test_password_too_short(self):
        """测试密码过短"""
        invalid_data = {
            "username": "testuser",
            "password": "12345",
            "confirm_password": "12345",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("at least 6 characters" in str(error['msg']) for error in errors)
    
    def test_password_no_letter(self):
        """测试密码不包含字母"""
        invalid_data = {
            "username": "testuser",
            "password": "123456789",
            "confirm_password": "123456789",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("必须包含至少一个字母" in str(error['msg']) for error in errors)
    
    def test_password_no_digit(self):
        """测试密码不包含数字"""
        invalid_data = {
            "username": "testuser",
            "password": "password",
            "confirm_password": "password",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("必须包含至少一个数字" in str(error['msg']) for error in errors)
    
    def test_password_mismatch(self):
        """测试密码不匹配"""
        invalid_data = {
            "username": "testuser",
            "password": "password123",
            "confirm_password": "password456",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("两次输入的密码不一致" in str(error['msg']) for error in errors)
    
    def test_invalid_email(self):
        """测试无效邮箱格式"""
        invalid_data = {
            "username": "testuser",
            "password": "password123",
            "confirm_password": "password123",
            "email": "invalid-email",
            "verification_code": "123456"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("value is not a valid email address" in str(error['msg']) for error in errors)
    
    def test_invalid_verification_code(self):
        """测试无效验证码"""
        invalid_data = {
            "username": "testuser",
            "password": "password123",
            "confirm_password": "password123",
            "email": "test@example.com",
            "verification_code": "abc123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("验证码必须为纯数字" in str(error['msg']) for error in errors)


class TestChangePasswordRequest:
    """修改密码请求模型测试"""
    
    def test_valid_change_password_data(self):
        """测试合法的修改密码数据"""
        valid_data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        request = ChangePasswordRequest(**valid_data)
        assert request.old_password == "oldpassword123"
        assert request.new_password == "newpassword123"
        assert request.confirm_password == "newpassword123"
    
    def test_new_password_same_as_old(self):
        """测试新密码与原密码相同"""
        invalid_data = {
            "old_password": "password123",
            "new_password": "password123",
            "confirm_password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("新密码不能与原密码相同" in str(error['msg']) for error in errors)
    
    def test_new_password_mismatch(self):
        """测试新密码确认不匹配"""
        invalid_data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword123",
            "confirm_password": "differentpassword123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("两次输入的密码不一致" in str(error['msg']) for error in errors)


class TestForgotPasswordRequest:
    """忘记密码请求模型测试"""
    
    def test_valid_forgot_password_data(self):
        """测试合法的忘记密码数据"""
        valid_data = {
            "email": "test@example.com",
            "verification_code": "123456",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        request = ForgotPasswordRequest(**valid_data)
        assert request.email == "test@example.com"
        assert request.verification_code == "123456"
        assert request.new_password == "newpassword123"
    
    def test_password_mismatch(self):
        """测试密码不匹配"""
        invalid_data = {
            "email": "test@example.com",
            "verification_code": "123456",
            "new_password": "newpassword123",
            "confirm_password": "differentpassword123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ForgotPasswordRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("两次输入的密码不一致" in str(error['msg']) for error in errors)


class TestBindEmailRequest:
    """绑定邮箱请求模型测试"""
    
    def test_valid_bind_email_data(self):
        """测试合法的绑定邮箱数据"""
        valid_data = {
            "email": "test@example.com",
            "verification_code": "123456",
            "password": "password123"
        }
        
        request = BindEmailRequest(**valid_data)
        assert request.email == "test@example.com"
        assert request.verification_code == "123456"
        assert request.password == "password123"
    
    def test_bind_email_without_password(self):
        """测试不提供密码的绑定邮箱"""
        valid_data = {
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        request = BindEmailRequest(**valid_data)
        assert request.email == "test@example.com"
        assert request.verification_code == "123456"
        assert request.password is None


class TestChangeEmailRequest:
    """修改邮箱请求模型测试"""
    
    def test_valid_change_email_data(self):
        """测试合法的修改邮箱数据"""
        valid_data = {
            "old_email": "old@example.com",
            "new_email": "new@example.com",
            "verification_code": "123456",
            "password": "password123"
        }
        
        request = ChangeEmailRequest(**valid_data)
        assert request.old_email == "old@example.com"
        assert request.new_email == "new@example.com"
        assert request.verification_code == "123456"
        assert request.password == "password123"
    
    def test_same_email_addresses(self):
        """测试新邮箱与原邮箱相同"""
        invalid_data = {
            "old_email": "test@example.com",
            "new_email": "test@example.com",
            "verification_code": "123456",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChangeEmailRequest(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any("新邮箱不能与原邮箱相同" in str(error['msg']) for error in errors)