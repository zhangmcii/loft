import pytest
import json
from flask import url_for
from app.models import Comment, Post, Permission

def test_get_comments(client):
    """测试获取所有评论"""
    response = client.get('/api/v1/comments/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert 'comments' in data['data']
    assert 'count' in data['data']

def test_get_comments_pagination(client, test_comment):
    """测试评论分页"""
    # 创建多个测试评论以测试分页
    from app import db
    from app.models import Comment
    
    # 创建10个额外的评论
    for i in range(10):
        comment = Comment(
            body=f'测试评论内容 {i}',
            author=test_comment.author,
            post=test_comment.post
        )
        db.session.add(comment)
    db.session.commit()
    
    # 测试第一页
    response = client.get('/api/v1/comments/?page=1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']['comments']) > 0
    
    # 如果有下一页，测试下一页
    if data['data']['next']:
        response = client.get(data['data']['next'])
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
    
    # 清理测试数据
    Comment.query.filter(Comment.body.like('测试评论内容%')).delete()
    db.session.commit()

def test_get_comment(client, test_comment):
    """测试获取指定评论"""
    response = client.get(f'/api/v1/comments/{test_comment.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data']['id'] == test_comment.id
    assert data['data']['body'] == test_comment.body

def test_get_comment_not_found(client):
    """测试获取不存在的评论"""
    response = client.get('/api/v1/comments/999')
    assert response.status_code == 404

def test_new_post_comment_success(client, test_token, test_post):
    """测试成功创建评论"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '测试API创建的评论'
    }
    
    # 模拟g.current_user
    with client.application.test_request_context():
        from flask import g
        from flask_jwt_extended import decode_token
        token_data = decode_token(test_token)
        from app.models import User
        g.current_user = User.query.get(token_data['sub'])
        
        response = client.post(f'/api/v1/posts/{test_post.id}/comments/', headers=headers, json=data)
        
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '评论创建成功'
    
    # 验证评论已创建
    comment = Comment.query.filter_by(body='测试API创建的评论').first()
    assert comment is not None
    assert comment.post_id == test_post.id
    
    # 清理测试数据
    Comment.query.filter_by(body='测试API创建的评论').delete()
    from app import db
    db.session.commit()

def test_new_post_comment_post_not_found(client, test_token):
    """测试对不存在的文章创建评论"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '测试评论'
    }
    response = client.post('/api/v1/posts/999/comments/', headers=headers, json=data)
    assert response.status_code == 404

def test_new_post_comment_unauthorized(client, test_post):
    """测试未授权创建评论"""
    data = {
        'body': '未授权评论'
    }
    response = client.post(f'/api/v1/posts/{test_post.id}/comments/', json=data)
    assert response.status_code == 401

def test_get_comments_new(client, test_post, test_comment):
    """测试获取文章的根评论及第一层回复"""
    response = client.get(f'/api/v1/posts/{test_post.id}/comments/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    assert 'reply' in data['data'][0]
    assert 'total' in data['extra']

def test_get_comments_new_post_not_found(client):
    """测试获取不存在文章的评论"""
    response = client.get('/api/v1/posts/999/comments/')
    assert response.status_code == 404

def test_get_comment_replies(client, test_comment):
    """测试获取指定评论的回复分页"""
    # 创建测试回复
    from app import db
    from app.models import Comment
    
    reply = Comment(
        body='测试回复内容',
        author=test_comment.author,
        post=test_comment.post,
        root_comment_id=test_comment.id
    )
    db.session.add(reply)
    db.session.commit()
    
    response = client.get(f'/api/v1/reply_comments/?rootCommentId={test_comment.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    assert data['data'][0]['content'] == '测试回复内容'
    assert 'total' in data['extra']
    
    # 清理测试数据
    Comment.query.filter_by(body='测试回复内容').delete()
    db.session.commit()

def test_get_comment_replies_pagination(client, test_comment):
    """测试评论回复分页"""
    # 创建多个测试回复以测试分页
    from app import db
    from app.models import Comment
    
    # 创建10个回复
    for i in range(10):
        reply = Comment(
            body=f'测试回复内容 {i}',
            author=test_comment.author,
            post=test_comment.post,
            root_comment_id=test_comment.id
        )
        db.session.add(reply)
    db.session.commit()
    
    # 测试第一页
    response = client.get(f'/api/v1/reply_comments/?rootCommentId={test_comment.id}&page=1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    
    # 如果有多页，测试第二页
    if data['extra']['total'] > len(data['data']):
        response = client.get(f'/api/v1/reply_comments/?rootCommentId={test_comment.id}&page=2')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
    
    # 清理测试数据
    Comment.query.filter(Comment.body.like('测试回复内容%')).delete()
    db.session.commit()