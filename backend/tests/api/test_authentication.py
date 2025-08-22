import pytest
import re
import json
from flask import url_for

def test_auth_middleware_skip_pattern(client):
    """测试API认证中间件对特定路径的放行"""
    # 测试不需要认证的路径
    response = client.get('/api/v1/posts/1')
    d = json.loads(response.data)
    # 应该不会返回401未授权错误
    assert d.get('code')  != 401
    
    response = client.get('/api/v1/users/1')
    d = json.loads(response.data)
    # 应该不会返回401未授权错误
    assert d.get('code') != 401

def test_auth_middleware_protected_routes(client):
    """测试API认证中间件对需要认证的路径的保护"""
    # 测试需要认证的路径
    response = client.get('/api/v1/search_followed')
    d = json.loads(response.data)
    # 应该返回401未授权错误
    assert d.get('code') == 401
    assert '未授权访问' in d.get('message') 

def test_auth_middleware_with_valid_token(client, test_token):
    """测试API认证中间件对带有有效令牌的请求的处理"""
    # 测试带有有效令牌的请求
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get('/api/v1/search_followed', headers=headers)
    # 不应该返回401未授权错误
    assert response.json.get('code') != 401