"""
数据校验工具函数测试
"""
import pytest
from unittest.mock import Mock, patch
from flask import Flask
from pydantic import BaseModel, Field
from app.utils.validation import validate_json, validate_form


# 测试用的Pydantic模型
class TestSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=10)
    age: int = Field(..., ge=0, le=120)


class TestValidateJson:
    """JSON数据校验装饰器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
    
    def test_valid_json_data(self):
        """测试合法的JSON数据"""
        with self.app.test_request_context(
            '/test',
            method='POST',
            json={'name': 'test', 'age': 25}
        ):
            @validate_json(TestSchema)
            def test_view(validated_data):
                return {'status': 'success', 'data': validated_data.dict()}
            
            result = test_view()
            assert result['status'] == 'success'
            assert result['data']['name'] == 'test'
            assert result['data']['age'] == 25
    
    def test_empty_json_data(self):
        """测试空JSON数据"""
        with self.app.test_request_context('/test', method='POST', json=None):
            @validate_json(TestSchema)
            def test_view(validated_data):
                return {'status': 'success'}
            
            with patch('app.utils.validation.response_error') as mock_response:
                mock_response.return_value = {'error': 'empty data'}
                result = test_view()
                mock_response.assert_called_once_with(400, "请求数据不能为空")
    
    def test_invalid_json_data(self):
        """测试无效的JSON数据"""
        with self.app.test_request_context(
            '/test',
            method='POST',
            json={'name': 'a', 'age': -1}  # name太短，age为负数
        ):
            @validate_json(TestSchema)
            def test_view(validated_data):
                return {'status': 'success'}
            
            with patch('app.utils.validation.response_error') as mock_response:
                mock_response.return_value = {'error': 'validation failed'}
                result = test_view()
                mock_response.assert_called_once()
                # 检查是否调用了response_error，参数应该是400和错误信息
                args, kwargs = mock_response.call_args
                assert args[0] == 400
                assert isinstance(args[1], str)


class TestValidateForm:
    """表单数据校验装饰器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
    
    def test_valid_form_data(self):
        """测试合法的表单数据"""
        with self.app.test_request_context(
            '/test',
            method='POST',
            data={'name': 'test', 'age': '25'}
        ):
            @validate_form(TestSchema)
            def test_view(validated_data):
                return {'status': 'success', 'data': validated_data.dict()}
            
            result = test_view()
            assert result['status'] == 'success'
            assert result['data']['name'] == 'test'
            assert result['data']['age'] == 25
    
    def test_empty_form_data(self):
        """测试空表单数据"""
        with self.app.test_request_context('/test', method='POST', data={}):
            @validate_form(TestSchema)
            def test_view(validated_data):
                return {'status': 'success'}
            
            with patch('app.utils.validation.response_error') as mock_response:
                mock_response.return_value = {'error': 'empty data'}
                result = test_view()
                mock_response.assert_called_once_with(400, "请求数据不能为空")
    
    def test_invalid_form_data(self):
        """测试无效的表单数据"""
        with self.app.test_request_context(
            '/test',
            method='POST',
            data={'name': 'a', 'age': '-1'}  # name太短，age为负数
        ):
            @validate_form(TestSchema)
            def test_view(validated_data):
                return {'status': 'success'}
            
            with patch('app.utils.validation.response_error') as mock_response:
                mock_response.return_value = {'error': 'validation failed'}
                result = test_view()
                mock_response.assert_called_once()
                # 检查是否调用了response_error
                args, kwargs = mock_response.call_args
                assert args[0] == 400
                assert isinstance(args[1], str)