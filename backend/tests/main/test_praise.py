import pytest
import json
from flask import url_for
from app.models import Praise, Notification, NotificationType

def test_praise_post_get(client, test_post):
    """测试获取文章点赞数"""
    response = client.get(f'/praise/{test_post.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert 'praise_total' in data['data']
    assert isinstance(data['data']['praise_total'], int)

def test_praise_post_success(client, test_token, test_user, test_post):
    """测试成功点赞文章"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.post(f'/praise/{test_post.id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data']['has_praised'] is True
    assert data['data']['praise_total'] > 0
    
    # 验证点赞记录已创建
    praise = Praise.query.filter_by(author_id=test_user.id, post_id=test_post.id).first()
    assert praise is not None
    
    # 清理测试数据
    Praise.query.filter_by(author_id=test_user.id, post_id=test_post.id).delete()

def test_praise_post_duplicate(client, test_token, test_user, test_post):
    """测试重复点赞文章"""
    # 先创建一个点赞
    praise = Praise(post=test_post, author=test_user)
    from app import db
    db.session.add(praise)
    db.session.commit()
    
    # 尝试再次点赞
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.post(f'/praise/{test_post.id}', headers=headers)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert data['message'] == '您已经点赞过了~'
    
    # 清理测试数据
    Praise.query.filter_by(author_id=test_user.id, post_id=test_post.id).delete()

def test_praise_post_unauthorized(client, test_post):
    """测试未授权点赞文章"""
    response = client.post(f'/praise/{test_post.id}')
    assert response.status_code == 401

def test_praise_post_notification(client, test_token, test_user, admin_user, monkeypatch):
    """测试点赞文章产生通知"""
    # 创建一个由管理员发布的文章
    from app.models import Post
    from app import db
    
    post = Post(body='测试通知的文章', author=admin_user)
    db.session.add(post)
    db.session.commit()
    
    # 模拟socketio.emit
    emitted_data = {}
    def mock_emit(event, data, to):
        emitted_data['event'] = event
        emitted_data['data'] = data
        emitted_data['to'] = to
    
    # 应用模拟
    monkeypatch.setattr('app.socketio.emit', mock_emit)
    
    # 普通用户点赞管理员的文章
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.post(f'/praise/{post.id}', headers=headers)
    assert response.status_code == 200
    
    # 验证通知已创建
    notification = Notification.query.filter_by(
        receiver_id=admin_user.id,
        trigger_user_id=test_user.id,
        post_id=post.id,
        type=NotificationType.LIKE
    ).first()
    assert notification is not None
    
    # 验证socketio事件已发送
    assert emitted_data.get('event') == 'new_notification'
    assert emitted_data.get('to') == str(admin_user.id)
    
    # 清理测试数据
    Notification.query.filter_by(post_id=post.id).delete()
    Praise.query.filter_by(post_id=post.id).delete()
    Post.query.filter_by(id=post.id).delete()

def test_praise_comment_get(client, test_comment):
    """测试获取评论点赞数"""
    response = client.get(f'/praise/comment/{test_comment.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert 'praise_total' in data['data']
    assert isinstance(data['data']['praise_total'], int)

def test_praise_comment_success(client, test_token, test_user, test_comment):
    """测试成功点赞评论"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.post(f'/praise/comment/{test_comment.id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data']['praise_total'] > 0
    
    # 验证点赞记录已创建
    praise = Praise.query.filter_by(author_id=test_user.id, comment_id=test_comment.id).first()
    assert praise is not None
    
    # 清理测试数据
    Praise.query.filter_by(author_id=test_user.id, comment_id=test_comment.id).delete()

def test_praise_comment_unauthorized(client, test_comment):
    """测试未授权点赞评论"""
    response = client.post(f'/praise/comment/{test_comment.id}')
    assert response.status_code == 401

def test_praise_comment_notification(client, test_token, test_user, admin_user, monkeypatch):
    """测试点赞评论产生通知"""
    # 创建一个由管理员发布的评论
    from app.models import Post, Comment
    from app import db
    
    post = Post(body='测试通知的文章', author=test_user)
    db.session.add(post)
    db.session.flush()
    
    comment = Comment(body='测试通知的评论', author=admin_user, post=post)
    db.session.add(comment)
    db.session.commit()
    
    # 模拟socketio.emit
    emitted_data = {}
    def mock_emit(event, data, to):
        emitted_data['event'] = event
        emitted_data['data'] = data
        emitted_data['to'] = to
    
    # 应用模拟
    monkeypatch.setattr('app.socketio.emit', mock_emit)
    
    # 普通用户点赞管理员的评论
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.post(f'/praise/comment/{comment.id}', headers=headers)
    assert response.status_code == 200
    
    # 验证通知已创建
    notification = Notification.query.filter_by(
        receiver_id=admin_user.id,
        trigger_user_id=test_user.id,
        comment_id=comment.id,
        type=NotificationType.LIKE
    ).first()
    assert notification is not None
    
    # 验证socketio事件已发送
    assert emitted_data.get('event') == 'new_notification'
    assert emitted_data.get('to') == str(admin_user.id)
    
    # 清理测试数据
    Notification.query.filter_by(comment_id=comment.id).delete()
    Praise.query.filter_by(comment_id=comment.id).delete()
    Comment.query.filter_by(id=comment.id).delete()
    Post.query.filter_by(id=post.id).delete()

def test_has_praised_comment_id(client, test_token, test_user, test_post, test_comment):
    """测试获取用户已点赞的评论ID列表"""
    # 创建点赞记录
    praise = Praise(comment=test_comment, author=test_user)
    from app import db
    db.session.add(praise)
    db.session.commit()
    
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get(f'/has_praised/{test_post.id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert test_comment.id in data['data']
    
    # 清理测试数据
    Praise.query.filter_by(author_id=test_user.id, comment_id=test_comment.id).delete()

def test_has_praised_comment_id_unauthorized(client, test_post):
    """测试未授权获取已点赞的评论ID列表"""
    response = client.get(f'/has_praised/{test_post.id}')
    assert response.status_code == 401