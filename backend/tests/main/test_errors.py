import pytest
import json
from flask import url_for

def test_missing_token_callback(client):
    """测试缺少令牌的回调函数"""
    # 访问需要JWT认证的路由，但不提供令牌
    response = client.get('/api/v1/protected')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['code'] == 401
    assert data['message'] == 'token无效'

def test_forbidden_error_handler(client):
    """测试403错误处理器"""
    # 创建一个测试路由，触发403错误
    with client.application.test_request_context():
        from app.main import main
        
        @main.route('/test_forbidden')
        def test_route():
            from flask import abort
            abort(403)
        
        # 访问测试路由
        response = client.get('/test_forbidden')
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['code'] == 403
        assert data['message'] == '权限不足'

def test_page_not_found_handler(client):
    """测试404错误处理器"""
    # 访问不存在的路由
    response = client.get('/nonexistent_route')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 404
    assert data['message'] == '资源不存在'

def test_too_many_requests_handler(client, monkeypatch):
    """测试429错误处理器"""
    # 创建一个测试路由，触发TooManyRequests错误
    with client.application.test_request_context():
        from app.main import main
        from werkzeug.exceptions import TooManyRequests
        
        @main.route('/test_too_many_requests')
        def test_route():
            raise TooManyRequests(description="请求过于频繁")
        
        # 访问测试路由
        response = client.get('/test_too_many_requests')
        assert response.status_code == 429
        data = json.loads(response.data)
        assert data['code'] == 429
        assert data['message'] == '请求频率超限'

def test_internal_server_error_handler(client):
    """测试500错误处理器"""
    # 创建一个测试路由，触发500错误
    with client.application.test_request_context():
        from app.main import main
        
        @main.route('/test_internal_error')
        def test_route():
            from flask import abort
            abort(500)
        
        # 访问测试路由
        response = client.get('/test_internal_error')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['code'] == 500
        assert data['message'] == '服务器内部错误'