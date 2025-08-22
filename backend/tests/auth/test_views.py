import pytest
import json
from flask import url_for
from app.models import User
from app import redis

def test_login_success(client, test_user):
    """测试登录成功"""
    data = {
        'uiAccountName': 'testuser',
        'uiPassword': 'password'
    }
    response = client.post('/auth/login', json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert 'token' in data
    assert data['data']['username'] == 'testuser'

def test_login_failure_wrong_password(client, test_user):
    """测试登录失败 - 密码错误"""
    data = {
        'uiAccountName': 'testuser',
        'uiPassword': 'wrong_password'
    }
    response = client.post('/auth/login', json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '账号或密码错误'

def test_login_failure_user_not_exist(client):
    """测试登录失败 - 用户不存在"""
    data = {
        'uiAccountName': 'nonexistent',
        'uiPassword': 'password'
    }
    response = client.post('/auth/login', json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '账号或密码错误'

def test_register_success(client):
    """测试注册成功"""
    data = {
        'username': 'newuser',
        'password': 'newpassword',
        'email': 'newuser@example.com'
    }
    response = client.post('/auth/register', json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证用户已创建
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'newuser@example.com'
    
    # 清理测试数据
    User.query.filter_by(username='newuser').delete()

def test_register_failure_username_exists(client, test_user):
    """测试注册失败 - 用户名已存在"""
    data = {
        'username': 'testuser',  # 已存在的用户名
        'password': 'newpassword',
        'email': 'another@example.com'
    }
    response = client.post('/auth/register', json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '该用户名已被注册，请换一个'

def test_register_failure_empty_password(client):
    """测试注册失败 - 空密码"""
    data = {
        'username': 'newuser',
        'password': '',
        'email': 'newuser@example.com'
    }
    response = client.post('/auth/register', json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '密码不能设置为空字符串'

def test_apply_code(client, test_token, monkeypatch):
    """测试申请验证码"""
    # 模拟发送邮件的函数
    def mock_delay(email, subject, **kwargs):
        return True
    
    # 模拟生成验证码的函数
    def mock_generate_code(email, expiration=180):
        return 123456
    
    # 应用模拟
    monkeypatch.setattr('app.mycelery.tasks.send_email.delay', mock_delay)
    monkeypatch.setattr('app.models.User.generate_code', mock_generate_code)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'email': 'test@example.com',
        'action': 'confirm'
    }
    response = client.post('/auth/applyCode', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200

def test_confirm_success(client, test_token, monkeypatch):
    """测试确认邮箱成功"""
    # 模拟验证码比较函数
    def mock_compare_code(email, code):
        return True
    
    # 应用模拟
    monkeypatch.setattr('app.models.User.compare_code', mock_compare_code)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'email': 'test@example.com',
        'code': '123456'
    }
    response = client.post('/auth/confirm', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data']['isConfirmed'] is True

def test_confirm_failure(client, test_token, monkeypatch):
    """测试确认邮箱失败 - 验证码错误"""
    # 模拟验证码比较函数
    def mock_compare_code(email, code):
        return False
    
    # 应用模拟
    monkeypatch.setattr('app.models.User.compare_code', mock_compare_code)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'email': 'test@example.com',
        'code': 'wrong_code'
    }
    response = client.post('/auth/confirm', headers=headers, json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '绑定失败'

def test_change_email_success(client, test_token, monkeypatch):
    """测试更改邮箱成功"""
    # 模拟验证码比较函数
    def mock_compare_code(email, code):
        return True
    
    # 应用模拟
    monkeypatch.setattr('app.models.User.compare_code', mock_compare_code)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'email': 'new_email@example.com',
        'code': '123456',
        'password': 'password'
    }
    response = client.post('/auth/changeEmail', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200

def test_change_email_failure_wrong_password(client, test_token):
    """测试更改邮箱失败 - 密码错误"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'email': 'new_email@example.com',
        'code': '123456',
        'password': 'wrong_password'
    }
    response = client.post('/auth/changeEmail', headers=headers, json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '密码错误'

def test_change_password_success(client, test_token):
    """测试更改密码成功"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'oldPassword': 'password',
        'newPassword': 'new_password'
    }
    response = client.post('/auth/changePassword', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证密码已更改
    user = User.query.filter_by(username='testuser').first()
    assert user.verify_password('new_password') is True
    
    # 恢复原密码以便其他测试
    user.password = 'password'

def test_change_password_failure_wrong_old_password(client, test_token):
    """测试更改密码失败 - 旧密码错误"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'oldPassword': 'wrong_password',
        'newPassword': 'new_password'
    }
    response = client.post('/auth/changePassword', headers=headers, json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '密码错误'

def test_change_password_failure_empty_new_password(client, test_token):
    """测试更改密码失败 - 新密码为空"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'oldPassword': 'password',
        'newPassword': ''
    }
    response = client.post('/auth/changePassword', headers=headers, json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '密码不能设置为空字符串'

def test_reset_password_success(client, monkeypatch):
    """测试重置密码成功"""
    # 模拟验证码比较函数
    def mock_compare_code(email, code):
        return True
    
    # 应用模拟
    monkeypatch.setattr('app.models.User.compare_code', mock_compare_code)
    
    data = {
        'email': 'test@example.com',
        'code': '123456',
        'password': 'reset_password'
    }
    response = client.post('/auth/resetPassword', json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证密码已重置
    user = User.query.filter_by(email='test@example.com').first()
    assert user.verify_password('reset_password') is True
    
    # 恢复原密码以便其他测试
    user.password = 'password'

def test_reset_password_failure_wrong_code(client, monkeypatch):
    """测试重置密码失败 - 验证码错误"""
    # 模拟验证码比较函数
    def mock_compare_code(email, code):
        return False
    
    # 应用模拟
    monkeypatch.setattr('app.models.User.compare_code', mock_compare_code)
    
    data = {
        'email': 'test@example.com',
        'code': 'wrong_code',
        'password': 'reset_password'
    }
    response = client.post('/auth/resetPassword', json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '验证码错误'

def test_help_change_password_success(client, admin_token, test_user):
    """测试管理员帮助更改密码成功"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    data = {
        'username': 'testuser',
        'newPassword': 'admin_reset_password'
    }
    response = client.post('/auth/helpChangePassword', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证密码已更改
    user = User.query.filter_by(username='testuser').first()
    assert user.verify_password('admin_reset_password') is True
    
    # 恢复原密码以便其他测试
    user.password = 'password'

def test_help_change_password_failure_not_admin(client, test_token):
    """测试非管理员帮助更改密码失败"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'username': 'admin',
        'newPassword': 'new_password'
    }
    response = client.post('/auth/helpChangePassword', headers=headers, json=data)
    assert response.status_code == 403  # 权限不足

def test_help_change_password_failure_user_not_exist(client, admin_token):
    """测试管理员帮助更改密码失败 - 用户不存在"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    data = {
        'username': 'nonexistent',
        'newPassword': 'new_password'
    }
    response = client.post('/auth/helpChangePassword', headers=headers, json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '用户不存在'