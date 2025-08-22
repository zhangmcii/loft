import pytest
import json
from flask import url_for
from app.exceptions import ValidationError

def test_validation_error(client):
    """测试ValidationError异常处理"""
    # 创建一个测试路由，触发ValidationError
    with client.application.test_request_context():
        from app.api import api
        
        @api.route('/test_validation_error')
        def test_route():
            raise ValidationError('测试验证错误')
        
        # 访问测试路由
        response = client.get('/api/v1/test_validation_error')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 400
        assert data['message'] == '测试验证错误'

def test_bad_request_response(client):
    """测试bad_request响应"""
    # 创建一个测试路由，返回bad_request
    with client.application.test_request_context():
        from app.api import api
        from app.utils.response import bad_request
        
        @api.route('/test_bad_request')
        def test_route():
            return bad_request('测试错误请求')
        
        # 访问测试路由
        response = client.get('/api/v1/test_bad_request')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['code'] == 400
        assert data['message'] == '测试错误请求'

def test_unauthorized_response(client):
    """测试unauthorized响应"""
    # 创建一个测试路由，返回unauthorized
    with client.application.test_request_context():
        from app.api import api
        from app.utils.response import unauthorized
        
        @api.route('/test_unauthorized')
        def test_route():
            return unauthorized('未授权访问')
        
        # 访问测试路由
        response = client.get('/api/v1/test_unauthorized')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['code'] == 401
        assert data['message'] == '未授权访问'

def test_forbidden_response(client):
    """测试forbidden响应"""
    # 创建一个测试路由，返回forbidden
    with client.application.test_request_context():
        from app.api import api
        from app.utils.response import forbidden
        
        @api.route('/test_forbidden')
        def test_route():
            return forbidden('禁止访问')
        
        # 访问测试路由
        response = client.get('/api/v1/test_forbidden')
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['code'] == 403
        assert data['message'] == '禁止访问'