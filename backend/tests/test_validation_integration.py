"""
校验工具与Flask集成测试
"""
import pytest
import json
from flask import Flask
from app.utils.validation import validate_request_data
from app.schemas.user_schemas import RegisterRequest
from app.utils.response import error


def create_test_app():
    """创建测试Flask应用"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


class TestValidationIntegration:
    """校验集成测试"""
    
    def test_validate_request_data_success(self):
        """测试请求数据校验成功"""
        app = create_test_app()
        
        with app.test_request_context(
            '/test',
            method='POST',
            data=json.dumps({
                "username": "testuser123",
                "password": "password123", 
                "email": "test@example.com"
            }),
            content_type='application/json'
        ):
            validated_data, error_response = validate_request_data(RegisterRequest)
            assert validated_data is not None
            assert error_response is None
            assert validated_data.username == "testuser123"
    
    def test_validate_request_data_validation_error(self):
        """测试请求数据校验失败"""
        app = create_test_app()
        
        with app.test_request_context(
            '/test',
            method='POST',
            data=json.dumps({
                "username": "ab",  # 用户名过短
                "password": "password123",
                "email": "test@example.com"
            }),
            content_type='application/json'
        ):
            validated_data, error_response = validate_request_data(RegisterRequest)
            assert validated_data is None
            assert error_response is not None
            assert error_response.status_code == 400
    
    def test_validate_request_data_no_json(self):
        """测试没有JSON数据的请求"""
        app = create_test_app()
        
        with app.test_request_context('/test', method='POST'):
            validated_data, error_response = validate_request_data(RegisterRequest)
            assert validated_data is None
            assert error_response is not None
            assert error_response.status_code == 400
    
    def test_validate_request_data_invalid_json(self):
        """测试无效JSON数据的请求"""
        app = create_test_app()
        
        with app.test_request_context(
            '/test',
            method='POST',
            data='invalid json',
            content_type='application/json'
        ):
            validated_data, error_response = validate_request_data(RegisterRequest)
            assert validated_data is None
            assert error_response is not None
            assert error_response.status_code == 400