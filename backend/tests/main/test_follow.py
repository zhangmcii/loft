import pytest
import json
from flask import url_for
from app.models import User, Follow

def test_follow_success(client, test_token, test_user, admin_user):
    """测试成功关注用户"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get(f'/follow/{admin_user.username}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证关注关系已建立
    is_following = test_user.is_following(admin_user)
    assert is_following is True
    
    # 清理测试数据
    test_user.unfollow(admin_user)

def test_follow_user_not_found(client, test_token):
    """测试关注不存在的用户"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get('/follow/nonexistent', headers=headers)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 404
    assert data['message'] == '用户名不存在'

def test_follow_already_following(client, test_token, test_user, admin_user, test_follow):
    """测试关注已关注的用户"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get(f'/follow/{admin_user.username}', headers=headers)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '你已经关注了该用户'

def test_follow_unauthorized(client, admin_user):
    """测试未授权关注用户"""
    response = client.get(f'/follow/{admin_user.username}')
    assert response.status_code == 401

def test_unfollow_success(client, test_token, test_user, admin_user, test_follow):
    """测试成功取消关注用户"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get(f'/unfollow/{admin_user.username}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证关注关系已解除
    is_following = test_user.is_following(admin_user)
    assert is_following is False
    
    # 恢复测试数据
    test_user.follow(admin_user)

def test_unfollow_user_not_found(client, test_token):
    """测试取消关注不存在的用户"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get('/unfollow/nonexistent', headers=headers)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 404
    assert data['message'] == '用户名不存在'

def test_unfollow_not_following(client, test_token, admin_user):
    """测试取消关注未关注的用户"""
    # 确保没有关注关系
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get(f'/unfollow/{admin_user.username}', headers=headers)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '你未关注该用户'

def test_unfollow_unauthorized(client, admin_user):
    """测试未授权取消关注用户"""
    response = client.get(f'/unfollow/{admin_user.username}')
    assert response.status_code == 401

def test_followers(client, test_user, admin_user, test_follow):
    """测试获取用户的粉丝列表"""
    # 让admin_user关注test_user
    admin_user.follow(test_user)
    
    response = client.get(f'/followers/{test_user.username}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    
    # 验证返回的粉丝数据
    follower = data['data'][0]
    assert follower['username'] == admin_user.username
    assert 'is_following' in follower
    
    # 清理测试数据
    admin_user.unfollow(test_user)

def test_followers_user_not_found(client):
    """测试获取不存在用户的粉丝列表"""
    response = client.get('/followers/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 404
    assert data['message'] == '用户名不存在'

def test_followed_by(client, test_user, admin_user, test_follow):
    """测试获取用户关注的人列表"""
    response = client.get(f'/followed_by/{test_user.username}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    
    # 验证返回的关注数据
    followed = data['data'][0]
    assert followed['username'] == admin_user.username
    assert 'is_following_back' in followed

def test_followed_by_user_not_found(client):
    """测试获取不存在用户关注的人列表"""
    response = client.get('/followed_by/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 404
    assert data['message'] == '用户名不存在'