import pytest
import json
from flask import url_for
from app.models import User, Role, Permission

def test_edit_profile_success(client, test_token, test_user):
    """测试成功编辑用户资料"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'nickname': '测试昵称',
        'location': '测试地点',
        'about_me': '测试个人简介'
    }
    response = client.post('/edit-profile', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '用户资料更新成功'
    
    # 验证用户资料已更新
    updated_user = User.query.get(test_user.id)
    assert updated_user.nickname == '测试昵称'
    assert updated_user.location == '测试地点'
    assert updated_user.about_me == '测试个人简介'

def test_edit_profile_unauthorized(client):
    """测试未授权编辑用户资料"""
    data = {
        'nickname': '未授权昵称',
        'location': '未授权地点',
        'about_me': '未授权个人简介'
    }
    response = client.post('/edit-profile', json=data)
    assert response.status_code == 401

def test_edit_profile_admin_success(client, admin_token, test_user):
    """测试管理员成功编辑用户资料"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    data = {
        'email': 'updated@example.com',
        'username': 'updated_username',
        'confirmed': True,
        'role': 1,  # 普通用户角色
        'nickname': '管理员更新的昵称',
        'location': '管理员更新的地点',
        'about_me': '管理员更新的个人简介'
    }
    response = client.post(f'/edit-profile/{test_user.id}', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '用户资料更新成功'
    
    # 验证用户资料已更新
    updated_user = User.query.get(test_user.id)
    assert updated_user.email == 'updated@example.com'
    assert updated_user.username == 'updated_username'
    assert updated_user.nickname == '管理员更新的昵称'
    
    # 恢复原始值以便其他测试
    updated_user.email = 'test@example.com'
    updated_user.username = 'testuser'

def test_edit_profile_admin_unauthorized(client, test_token, test_user):
    """测试非管理员编辑他人资料被禁止"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'email': 'unauthorized@example.com',
        'username': 'unauthorized_username',
        'confirmed': True,
        'role': 1
    }
    response = client.post(f'/edit-profile/{test_user.id}', headers=headers, json=data)
    assert response.status_code == 403

def test_add_user_image_success(client, test_token):
    """测试成功添加用户头像"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'image': 'test_avatar.jpg'
    }
    response = client.post('/image', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert 'image' in data['data']
    
    # 验证用户头像已更新
    user = User.query.filter_by(username='testuser').first()
    assert user.image == 'test_avatar.jpg'

def test_add_user_image_unauthorized(client):
    """测试未授权添加用户头像"""
    data = {
        'image': 'unauthorized_avatar.jpg'
    }
    response = client.post('/image', json=data)
    assert response.status_code == 401

def test_get_user_by_username_success(client, test_user):
    """测试成功通过用户名获取用户信息"""
    response = client.get(f'/users/{test_user.username}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data']['username'] == test_user.username
    # 非管理员访问，不应包含敏感信息
    assert 'email' not in data['data']
    assert 'confirmed' not in data['data']

def test_get_user_by_username_admin(client, admin_token, test_user):
    """测试管理员通过用户名获取用户信息（包含敏感信息）"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get(f'/users/{test_user.username}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data']['username'] == test_user.username
    # 管理员访问，应包含敏感信息
    assert 'email' in data['data']
    assert 'confirmed' in data['data']

def test_get_user_by_username_not_found(client):
    """测试获取不存在用户的信息"""
    response = client.get('/users/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 404
    assert data['message'] == '用户不存在'

def test_can_permission(client, test_token):
    """测试检查用户权限"""
    headers = {'Authorization': f'Bearer {test_token}'}
    # 测试普通用户的写权限（应该有）
    response = client.get(f'/can/{Permission.WRITE}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data'] is True
    
    # 测试普通用户的管理员权限（应该没有）
    response = client.get(f'/can/{Permission.ADMIN}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data'] is False

def test_can_permission_admin(client, admin_token):
    """测试检查管理员权限"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    # 测试管理员的管理员权限（应该有）
    response = client.get(f'/can/{Permission.ADMIN}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data'] is True

def test_can_permission_unauthorized(client):
    """测试未登录用户检查权限"""
    # 未登录用户应该没有任何权限
    response = client.get(f'/can/{Permission.WRITE}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data'] is False

def test_generate_user_posts_admin(client, admin_token, monkeypatch):
    """测试管理员生成用户和文章"""
    # 模拟Fake类的方法
    def mock_users():
        return True
    
    def mock_posts():
        return True
    
    # 应用模拟
    monkeypatch.setattr('app.fake.Fake.users', mock_users)
    monkeypatch.setattr('app.fake.Fake.posts', mock_posts)
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/user_posts', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '用户和文章生成成功'

def test_generate_user_posts_unauthorized(client, test_token):
    """测试非管理员生成用户和文章被禁止"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get('/user_posts', headers=headers)
    assert response.status_code == 403