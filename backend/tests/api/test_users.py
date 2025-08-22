import pytest
import json
from flask import url_for

def test_get_user(client, test_user):
    """测试获取用户信息"""
    response = client.get(f'/api/v1/users/{test_user.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data']['username'] == test_user.username

def test_get_user_not_found(client):
    """测试获取不存在的用户信息"""
    response = client.get('/api/v1/users/999')
    assert response.status_code == 404

def test_get_user_posts(client, test_user, test_post):
    """测试获取用户文章列表"""
    response = client.get(f'/api/v1/users/{test_user.id}/posts/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']['posts']) > 0
    assert data['data']['posts'][0]['author'] == test_user.username

def test_get_user_followed_posts(client, test_user, test_post, test_follow):
    """测试获取用户关注的文章列表"""
    response = client.get(f'/api/v1/users/{test_user.id}/timeline/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    # 验证返回的数据结构
    assert 'posts' in data['data']
    assert 'count' in data['data']

def test_search_followed(client, test_token, test_user, admin_user, test_follow):
    """测试搜索关注的用户"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get('/api/v1/search_followed?name=admin', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    assert data['data'][0]['username'] == admin_user.username

def test_search_followed_unauthorized(client):
    """测试未授权搜索关注的用户"""
    response = client.get('/api/v1/search_followed?name=admin')
    assert response.status_code == 401

def test_search_fan(client, test_token, test_user, admin_user, test_follow):
    """测试搜索粉丝"""
    # 让admin_user关注test_user
    admin_user.follow(test_user)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get('/api/v1/search_fan?name=admin', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 清理测试数据
    admin_user.unfollow(test_user)

def test_update_user_profile(client, test_token, test_user):
    """测试更新用户信息"""
    headers = {
        'Authorization': f'Bearer {test_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'nickname': '新昵称',
        'about_me': '新的个人简介',
        'location': '新的位置'
    }
    response = client.post('/api/v1/update_user', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '用户信息更新成功'
    
    # 验证用户信息已更新
    updated_user = test_user
    assert updated_user.nickname == '新昵称'
    assert updated_user.about_me == '新的个人简介'
    assert updated_user.location == '新的位置'

def test_update_user_profile_unauthorized(client):
    """测试未授权更新用户信息"""
    data = {
        'nickname': '新昵称',
        'about_me': '新的个人简介',
        'location': '新的位置'
    }
    response = client.post('/api/v1/update_user', json=data)
    assert response.status_code == 401