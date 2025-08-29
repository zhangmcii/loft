"""
用户校验集成测试
测试API接口与Pydantic校验的完整流程
"""
import pytest
import json
from flask import Flask
from unittest.mock import patch
from app.api.user_validation_example import user_validation_bp


class TestUserValidationIntegration:
    """用户校验集成测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(user_validation_bp)
        self.client = self.app.test_client()
    
    def test_register_success(self):
        """测试注册成功"""
        valid_data = {
            "username": "testuser123",
            "password": "password123",
            "confirm_password": "password123",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        with patch('app.utils.response.response_success') as mock_success:
            mock_success.return_value = {'code': 200, 'message': '注册成功'}
            
            response = self.client.post(
                '/api/user/register',
                data=json.dumps(valid_data),
                content_type='application/json'
            )
            
            mock_success.assert_called_once()
    
    def test_register_validation_error(self):
        """测试注册数据校验失败"""
        invalid_data = {
            "username": "ab",  # 用户名过短
            "password": "password123",
            "confirm_password": "password123",
            "email": "test@example.com",
            "verification_code": "123456"
        }
        
        with patch('app.utils.response.response_error') as mock_error:
            mock_error.return_value = {'code': 400, 'message': '校验失败'}
            
            response = self.client.post(
                '/api/user/register',
                data=json.dumps(invalid_data),
                content_type='application/json'
            )
            
            mock_error.assert_called_once()
            args, kwargs = mock_error.call_args
            assert args[0] == 400
    
    def test_change_password_success(self):
        """测试修改密码成功"""
        valid_data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        with patch('app.utils.response.response_success') as mock_success:
            mock_success.return_value = {'code': 200, 'message': '密码修改成功'}
            
            response = self.client.post(
                '/api/user/change-password',
                data=json.dumps(valid_data),
                content_type='application/json'
            )
            
            mock_success.assert_called_once()
    
    def test_change_password_validation_error(self):
        """测试修改密码校验失败"""
        invalid_data = {
            "old_password": "password123",
            "new_password": "password123",  # 新密码与原密码相同
            "confirm_password": "password123"
        }
        
        with patch('app.utils.response.response_error') as mock_error:
            mock_error.return_value = {'code': 400, 'message': '校验失败'}
            
            response = self.client.post(
                '/api/user/change-password',
                data=json.dumps(invalid_data),
                content_type='application/json'
            )
            
            mock_error.assert_called_once()
    
    def test_forgot_password_success(self):
        """测试忘记密码成功"""
        valid_data = {
            "email": "test@example.com",
            "verification_code": "123456",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        with patch('app.utils.response.response_success') as mock_success:
            mock_success.return_value = {'code': 200, 'message': '密码重置成功'}
            
            response = self.client.post(
                '/api/user/forgot-password',
                data=json.dumps(valid_data),
                content_type='application/json'
            )
            
            mock_success.assert_called_once()
    
    def test_bind_email_success(self):
        """测试绑定邮箱成功"""
        valid_data = {
            "email": "test@example.com",
            "verification_code": "123456",
            "password": "password123"
        }
        
        with patch('app.utils.response.response_success') as mock_success:
            mock_success.return_value = {'code': 200, 'message': '邮箱绑定成功'}
            
            response = self.client.post(
                '/api/user/bind-email',
                data=json.dumps(valid_data),
                content_type='application/json'
            )
            
            mock_success.assert_called_once()
    
    def test_change_email_success(self):
        """测试修改邮箱成功"""
        valid_data = {
            "old_email": "old@example.com",
            "new_email": "new@example.com",
            "verification_code": "123456",
            "password": "password123"
        }
        
        with patch('app.utils.response.response_success') as mock_success:
            mock_success.return_value = {'code': 200, 'message': '邮箱修改成功'}
            
            response = self.client.post(
                '/api/user/change-email',
                data=json.dumps(valid_data),
                content_type='application/json'
            )
            
            mock_success.assert_called_once()
    
    def test_change_email_validation_error(self):
        """测试修改邮箱校验失败"""
        invalid_data = {
            "old_email": "test@example.com",
            "new_email": "test@example.com",  # 新邮箱与原邮箱相同
            "verification_code": "123456",
            "password": "password123"
        }
        
        with patch('app.utils.response.response_error') as mock_error:
            mock_error.return_value = {'code': 400, 'message': '校验失败'}
            
            response = self.client.post(
                '/api/user/change-email',
                data=json.dumps(invalid_data),
                content_type='application/json'
            )
            
            mock_error.assert_called_once()
    
    def test_empty_request_data(self):
        """测试空请求数据"""
        with patch('app.utils.response.response_error') as mock_error:
            mock_error.return_value = {'code': 400, 'message': '请求数据不能为空'}
            
            response = self.client.post(
                '/api/user/register',
                data='',
                content_type='application/json'
            )
            
            mock_error.assert_called_once()
            args, kwargs = mock_error.call_args
            assert args[0] == 400
            assert "请求数据不能为空" in args[1]
    
    def test_invalid_json_format(self):
        """测试无效的JSON格式"""
        with patch('app.utils.response.response_error') as mock_error:
            mock_error.return_value = {'code': 400, 'message': '数据校验失败'}
            
            response = self.client.post(
                '/api/user/register',
                data='invalid json',
                content_type='application/json'
            )
            
            # 由于JSON解析失败，Flask会返回400错误
            # 这里主要测试我们的错误处理机制