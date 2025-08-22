import pytest
import json
from flask import url_for
from app.models import Notification, NotificationType

def test_get_currentUsernotification(client, test_token, test_user):
    """测试获取当前用户的所有通知"""
    # 创建测试通知
    from app import db
    notification = Notification(
        receiver_id=test_user.id,
        trigger_user_id=test_user.id,
        type=NotificationType.COMMENT
    )
    db.session.add(notification)
    db.session.commit()
    
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get('/notifications', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    assert data['data'][0]['id'] == notification.id
    
    # 清理测试数据
    Notification.query.filter_by(id=notification.id).delete()
    db.session.commit()

def test_get_currentUsernotification_unauthorized(client):
    """测试未授权获取通知"""
    response = client.get('/notifications')
    assert response.status_code == 401

def test_mark_read_notification(client, test_token, test_user):
    """测试标记通知为已读"""
    # 创建测试通知
    from app import db
    notification = Notification(
        receiver_id=test_user.id,
        trigger_user_id=test_user.id,
        type=NotificationType.COMMENT,
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()
    
    headers = {
        'Authorization': f'Bearer {test_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'ids': [notification.id]
    }
    response = client.post('/notification/read', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '通知已标记为已读'
    
    # 验证通知已标记为已读
    updated_notification = Notification.query.get(notification.id)
    assert updated_notification.is_read is True
    
    # 清理测试数据
    Notification.query.filter_by(id=notification.id).delete()
    db.session.commit()

def test_mark_read_notification_unauthorized(client):
    """测试未授权标记通知为已读"""
    data = {
        'ids': [1]
    }
    response = client.post('/notification/read', json=data)
    assert response.status_code == 401

def test_new_post_notification(client, test_token, test_user, admin_user, monkeypatch):
    """测试创建新文章通知"""
    # 创建关注关系
    from app.models import Follow
    from app import db
    
    # admin_user关注test_user
    follow = Follow(follower=admin_user, followed=test_user)
    db.session.add(follow)
    db.session.commit()
    
    # 模拟socketio.emit
    emitted_data = {}
    def mock_emit(event, data, to):
        emitted_data['event'] = event
        emitted_data['data'] = data
        emitted_data['to'] = to
    
    # 应用模拟
    monkeypatch.setattr('app.socketio.emit', mock_emit)
    
    # 创建文章并触发通知
    from app.models import Post
    from app.main.notifications import new_post_notification
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '测试通知的文章',
        'bodyHtml': None,
        'images': []
    }
    response = client.post('/', headers=headers, json=data)
    assert response.status_code == 200
    
    # 获取创建的文章ID
    post = Post.query.filter_by(body='测试通知的文章').first()
    assert post is not None
    
    # 手动调用通知函数
    with client.application.test_request_context():
        from flask_jwt_extended import set_access_cookies
        from flask import g
        g.current_user = test_user
        new_post_notification(post.id)
    
    # 验证通知已创建
    notification = Notification.query.filter_by(
        receiver_id=admin_user.id,
        trigger_user_id=test_user.id,
        post_id=post.id,
        type=NotificationType.NewPost
    ).first()
    assert notification is not None
    
    # 验证socketio事件已发送
    assert emitted_data.get('event') == 'new_notification'
    assert emitted_data.get('to') == str(admin_user.id)
    
    # 清理测试数据
    Notification.query.filter_by(post_id=post.id).delete()
    Post.query.filter_by(id=post.id).delete()
    Follow.query.filter_by(follower_id=admin_user.id, followed_id=test_user.id).delete()
    db.session.commit()

def test_online_admin(client, admin_token, monkeypatch):
    """测试管理员获取在线用户信息"""
    # 模拟ManageSocket类
    class MockManageSocket:
        def __init__(self):
            from app.models import User
            user = User.query.first()
            self.user_socket = {user.id: 'socket_id'}
    
    # 应用模拟
    monkeypatch.setattr('app.utils.socket_util.ManageSocket', MockManageSocket)
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/socketData', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    assert 'username' in data['data'][0]
    assert 'total' in data['extra']
    assert data['extra']['total'] == len(data['data'])

def test_online_unauthorized(client):
    """测试未授权获取在线用户信息"""
    response = client.get('/socketData')
    assert response.status_code == 401

def test_online_forbidden(client, test_token):
    """测试非管理员获取在线用户信息被禁止"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get('/socketData', headers=headers)
    assert response.status_code == 403