import pytest
import json
from flask import url_for
from app.models import Permission

def test_permission_required_with_permission(client, test_token, test_user):
    """测试具有权限时的权限检查装饰器"""
    # 创建一个测试路由，使用permission_required装饰器
    with client.application.test_request_context():
        from app.api import api
        from app.api.decorators import permission_required
        
        @api.route('/test_permission')
        @permission_required(Permission.WRITE)  # 普通用户应该有写权限
        def test_route():
            from flask import jsonify
            return jsonify({'success': True})
        
        # 访问测试路由，带有有效令牌
        headers = {'Authorization': f'Bearer {test_token}'}
        response = client.get('/api/v1/test_permission', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

def test_permission_required_without_permission(client, test_token, test_user, monkeypatch):
    """测试没有权限时的权限检查装饰器"""
    # 创建一个测试路由，使用permission_required装饰器
    with client.application.test_request_context():
        from app.api import api
        from app.api.decorators import permission_required
        
        # 模拟用户没有权限
        def mock_can(permission):
            return False
        
        # 应用模拟
        monkeypatch.setattr('app.models.User.can', mock_can)
        
        @api.route('/test_no_permission')
        @permission_required(Permission.ADMIN)  # 要求管理员权限
        def test_route():
            from flask import jsonify
            return jsonify({'success': True})
        
        # 访问测试路由，带有有效令牌但没有足够权限
        headers = {'Authorization': f'Bearer {test_token}'}
        response = client.get('/api/v1/test_no_permission', headers=headers)
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['code'] == 403
        assert data['message'] == 'Insufficient permissions'

def test_permission_required_unauthorized(client):
    """测试未授权访问需要权限的路由"""
    # 创建一个测试路由，使用permission_required装饰器
    with client.application.test_request_context():
        from app.api import api
        from app.api.decorators import permission_required
        
        @api.route('/test_unauthorized_permission')
        @permission_required(Permission.WRITE)
        def test_route():
            from flask import jsonify
            return jsonify({'success': True})
        
        # 访问测试路由，不带令牌
        response = client.get('/api/v1/test_unauthorized_permission')
        assert response.status_code == 401