import pytest
import json
from flask import url_for
from app.models import Comment

def test_get_comments(client, test_post, test_comment):
    """测试获取文章评论"""
    response = client.get(f'/comments/{test_post.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']['comments']) > 0
    assert data['data']['comments'][0]['id'] == test_comment.id
    assert data['data']['comments'][0]['body'] == test_comment.body

def test_get_comments_post_not_found(client):
    """测试获取不存在文章的评论"""
    response = client.get('/comments/999')
    assert response.status_code == 404

def test_add_comment_success(client, test_token, test_post):
    """测试成功添加评论"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '测试添加的评论'
    }
    response = client.post(f'/comments/{test_post.id}', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证评论已添加
    comment = Comment.query.filter_by(body='测试添加的评论').first()
    assert comment is not None
    assert comment.post_id == test_post.id
    
    # 清理测试数据
    Comment.query.filter_by(body='测试添加的评论').delete()

def test_add_comment_unauthorized(client, test_post):
    """测试未授权添加评论"""
    data = {
        'body': '未授权添加的评论'
    }
    response = client.post(f'/comments/{test_post.id}', json=data)
    assert response.status_code == 401
    
    # 验证评论未添加
    comment = Comment.query.filter_by(body='未授权添加的评论').first()
    assert comment is None

def test_add_reply_success(client, test_token, test_comment):
    """测试成功添加回复"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '测试添加的回复',
        'comment_id': test_comment.id
    }
    response = client.post(f'/reply/{test_comment.post_id}', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证回复已添加
    reply = Comment.query.filter_by(body='测试添加的回复').first()
    assert reply is not None
    assert reply.post_id == test_comment.post_id
    assert reply.root_comment_id == test_comment.id
    
    # 清理测试数据
    Comment.query.filter_by(body='测试添加的回复').delete()

def test_add_reply_unauthorized(client, test_comment):
    """测试未授权添加回复"""
    data = {
        'body': '未授权添加的回复',
        'comment_id': test_comment.id
    }
    response = client.post(f'/reply/{test_comment.post_id}', json=data)
    assert response.status_code == 401
    
    # 验证回复未添加
    reply = Comment.query.filter_by(body='未授权添加的回复').first()
    assert reply is None

def test_moderate_comment_success(client, admin_token, test_comment):
    """测试管理员成功禁用评论"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post(f'/moderate/enable/{test_comment.id}/0', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证评论已禁用
    comment = Comment.query.get(test_comment.id)
    assert comment.disabled is True
    
    # 恢复评论状态
    comment.disabled = False

def test_moderate_comment_unauthorized(client, test_comment):
    """测试未授权禁用评论"""
    response = client.post(f'/moderate/enable/{test_comment.id}/0')
    assert response.status_code == 401
    
    # 验证评论状态未变
    comment = Comment.query.get(test_comment.id)
    assert comment.disabled is False

def test_moderate_comment_forbidden(client, test_token, test_comment):
    """测试非管理员禁用评论被禁止"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.post(f'/moderate/enable/{test_comment.id}/0', headers=headers)
    assert response.status_code == 403
    
    # 验证评论状态未变
    comment = Comment.query.get(test_comment.id)
    assert comment.disabled is False

def test_delete_comment_success(client, admin_token, test_comment):
    """测试管理员成功删除评论"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # 创建一个临时评论用于删除测试
    temp_comment = Comment(
        body='临时评论用于删除测试',
        author_id=test_comment.author_id,
        post_id=test_comment.post_id
    )
    from app import db
    db.session.add(temp_comment)
    db.session.commit()
    
    response = client.delete(f'/comments/{temp_comment.id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证评论已删除
    deleted_comment = Comment.query.get(temp_comment.id)
    assert deleted_comment is None

def test_delete_comment_unauthorized(client, test_comment):
    """测试未授权删除评论"""
    response = client.delete(f'/comments/{test_comment.id}')
    assert response.status_code == 401
    
    # 验证评论未删除
    comment = Comment.query.get(test_comment.id)
    assert comment is not None

def test_delete_comment_forbidden(client, test_token, admin_user, test_comment):
    """测试非作者和非管理员删除评论被禁止"""
    # 修改评论作者为管理员
    test_comment.author = admin_user
    
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.delete(f'/comments/{test_comment.id}', headers=headers)
    assert response.status_code == 403
    
    # 验证评论未删除
    comment = Comment.query.get(test_comment.id)
    assert comment is not None
    
    # 恢复评论作者