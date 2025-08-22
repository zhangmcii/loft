import pytest
import json
from flask import url_for
from app.models import Post, PostType, Image, ImageType

def test_index_get(client, test_post):
    """测试获取文章列表"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    assert data['data'][0]['id'] == test_post.id
    assert data['data'][0]['body'] == test_post.body

def test_index_post_success(client, test_token):
    """测试成功创建文章"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '测试创建新文章',
        'bodyHtml': None,
        'images': []
    }
    response = client.post('/', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证文章已创建
    post = Post.query.filter_by(body='测试创建新文章').first()
    assert post is not None
    assert post.type == PostType.TEXT
    
    # 清理测试数据
    Post.query.filter_by(body='测试创建新文章').delete()

def test_index_post_with_images(client, test_token):
    """测试创建带图片的文章"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '测试创建带图片的文章',
        'bodyHtml': '<p>测试创建带图片的文章</p><img src="1" alt="测试图片">',
        'images': [
            {'url': 'test_image_url.jpg', 'pos': '1'}
        ]
    }
    response = client.post('/', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证文章和图片已创建
    post = Post.query.filter_by(body='测试创建带图片的文章').first()
    assert post is not None
    assert post.type == PostType.IMAGE
    
    # 验证图片已关联到文章
    image = Image.query.filter_by(related_id=post.id).first()
    assert image is not None
    assert image.url == 'test_image_url.jpg'
    assert image.type == ImageType.POST
    
    # 清理测试数据
    Image.query.filter_by(related_id=post.id).delete()
    Post.query.filter_by(body='测试创建带图片的文章').delete()

def test_index_post_unauthorized(client):
    """测试未授权创建文章"""
    data = {
        'body': '未授权创建文章',
        'bodyHtml': None,
        'images': []
    }
    response = client.post('/', json=data)
    # 由于auth.before_app_request中使用了jwt_required(optional=True)，
    # 这里不会返回401，但会因为权限不足而无法创建文章
    assert response.status_code == 200
    # 验证文章未创建
    post = Post.query.filter_by(body='未授权创建文章').first()
    assert post is None

def test_user_posts(client, test_user, test_post):
    """测试获取用户文章"""
    response = client.get(f'/user/{test_user.username}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']['posts']) > 0
    assert data['data']['posts'][0]['id'] == test_post.id
    assert data['data']['posts'][0]['author'] == test_user.username

def test_user_posts_user_not_found(client):
    """测试获取不存在用户的文章"""
    response = client.get('/user/nonexistent')
    assert response.json.get('code') == 404
    data = json.loads(response.data)
    assert data['code'] == 404
    assert data['message'] == '用户不存在'

def test_edit_post_success(client, test_token, test_post):
    """测试成功编辑文章"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '已编辑的文章内容',
        'bodyHtml': '<p>已编辑的文章内容</p>'
    }
    response = client.put(f'/edit/{test_post.id}', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '文章编辑成功'
    
    # 验证文章已更新
    updated_post = Post.query.get(test_post.id)
    assert updated_post.body == '已编辑的文章内容'
    assert updated_post.body_html == '<p>已编辑的文章内容</p>'

def test_edit_post_unauthorized(client, test_post):
    """测试未授权编辑文章"""
    data = {
        'body': '未授权编辑的文章内容',
        'bodyHtml': '<p>未授权编辑的文章内容</p>'
    }
    response = client.put(f'/edit/{test_post.id}', json=data)
    assert response.status_code == 401
    
    # 验证文章未更新
    unchanged_post = Post.query.get(test_post.id)
    assert unchanged_post.body != '未授权编辑的文章内容'

def test_edit_post_forbidden(client, admin_user, test_token, test_post):
    """测试编辑他人文章被禁止"""
    # 修改文章作者为管理员
    test_post.author = admin_user
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '尝试编辑他人文章',
        'bodyHtml': '<p>尝试编辑他人文章</p>'
    }
    response = client.put(f'/edit/{test_post.id}', headers=headers, json=data)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['code'] == 403
    assert data['message'] == '没有权限编辑此文章'
    
    # 恢复文章作者

def test_create_rich_post_success(client, test_token):
    """测试成功创建富文本文章"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'content': '测试富文本文章内容',
        'imageUrls': ['rich_test_image1.jpg', 'rich_test_image2.jpg']
    }
    response = client.post('/rich_post', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证文章已创建
    post = Post.query.filter_by(body='测试富文本文章内容').first()
    assert post is not None
    assert post.type == PostType.IMAGE
    
    # 验证图片已关联到文章
    images = Image.query.filter_by(related_id=post.id).all()
    assert len(images) == 2
    assert images[0].url == 'rich_test_image1.jpg'
    assert images[1].url == 'rich_test_image2.jpg'
    
    # 清理测试数据
    Image.query.filter_by(related_id=post.id).delete()
    Post.query.filter_by(body='测试富文本文章内容').delete()

def test_create_rich_post_rate_limit(client, test_token, monkeypatch):
    """测试富文本文章创建的速率限制"""
    # 模拟速率限制异常
    def mock_limit(*args, **kwargs):
        from werkzeug.exceptions import TooManyRequests
        raise TooManyRequests()
    
    # 应用模拟
    monkeypatch.setattr('app.limiter.limit', mock_limit)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'content': '测试速率限制',
        'imageUrls': []
    }
    
    # 这里应该会触发速率限制异常
    with pytest.raises(Exception):
        response = client.post('/rich_post', headers=headers, json=data)