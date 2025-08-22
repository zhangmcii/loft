import pytest
import json
from flask import url_for
from app.models import Post, Permission, Image, ImageType, PostType

def test_get_posts(client):
    """测试获取所有文章"""
    response = client.get('/api/v1/posts/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert 'posts' in data['data']
    assert 'count' in data['data']

def test_get_posts_pagination(client, test_post):
    """测试文章分页"""
    # 创建多个测试文章以测试分页
    from app import db
    from app.models import Post
    
    # 创建10个额外的文章
    for i in range(10):
        post = Post(
            body=f'测试文章内容 {i}',
            author=test_post.author
        )
        db.session.add(post)
    db.session.commit()
    
    # 测试第一页
    response = client.get('/api/v1/posts/?page=1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']['posts']) > 0
    
    # 如果有下一页，测试下一页
    if data['data']['next']:
        response = client.get(data['data']['next'])
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
    
    # 清理测试数据
    Post.query.filter(Post.body.like('测试文章内容%')).delete()
    db.session.commit()

def test_get_post(client, test_post):
    """测试获取指定文章"""
    response = client.get(f'/api/v1/posts/{test_post.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data']['id'] == test_post.id
    assert data['data']['body'] == test_post.body

def test_get_post_not_found(client):
    """测试获取不存在的文章"""
    response = client.get('/api/v1/posts/999')
    assert response.status_code == 404

def test_new_post(client, test_token):
    """测试创建新文章"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '测试API创建的文章'
    }
    
    # 模拟current_user
    with client.application.test_request_context():
        from flask import g
        from flask_jwt_extended import decode_token
        token_data = decode_token(test_token)
        from app.models import User
        current_user = User.query.get(token_data['sub'])
        
        response = client.post('/api/v1/posts/', headers=headers, json=data)
        
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证文章已创建
    post = Post.query.filter_by(body='测试API创建的文章').first()
    assert post is not None
    
    # 清理测试数据
    Post.query.filter_by(body='测试API创建的文章').delete()
    from app import db
    db.session.commit()

def test_edit_post_success(client, test_token, test_post):
    """测试成功编辑文章"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '已编辑的文章内容',
        'bodyHtml': '<p>已编辑的文章内容</p>'
    }
    response = client.put(f'/api/v1/posts/{test_post.id}', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证文章已更新
    updated_post = Post.query.get(test_post.id)
    assert updated_post.body == '已编辑的文章内容'
    assert updated_post.body_html == '<p>已编辑的文章内容</p>'

def test_edit_post_with_images(client, test_token, test_post):
    """测试编辑文章并添加图片"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '带图片的文章内容',
        'bodyHtml': '<p>带图片的文章内容</p><img src="1" alt="测试图片">',
        'images': [
            {'url': 'test_image_url.jpg', 'pos': '1'}
        ]
    }
    response = client.put(f'/api/v1/posts/{test_post.id}', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    
    # 验证文章和图片已更新
    updated_post = Post.query.get(test_post.id)
    assert updated_post.body == '带图片的文章内容'
    
    # 验证图片已关联到文章
    image = Image.query.filter_by(related_id=test_post.id).first()
    assert image is not None
    assert image.url == 'test_image_url.jpg'
    assert image.type == ImageType.POST
    
    # 清理测试数据
    Image.query.filter_by(related_id=test_post.id).delete()
    from app import db
    db.session.commit()

def test_edit_post_unauthorized(client, test_post):
    """测试未授权编辑文章"""
    data = {
        'body': '未授权编辑的文章内容'
    }
    response = client.put(f'/api/v1/posts/{test_post.id}', json=data)
    assert response.status_code == 401
    
    # 验证文章未更新
    unchanged_post = Post.query.get(test_post.id)
    assert unchanged_post.body != '未授权编辑的文章内容'

def test_edit_post_forbidden(client, admin_user, test_token, test_post):
    """测试编辑他人文章被禁止"""
    # 修改文章作者为管理员
    test_post.author = admin_user
    from app import db
    db.session.commit()
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'body': '尝试编辑他人文章'
    }
    response = client.put(f'/api/v1/posts/{test_post.id}', headers=headers, json=data)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['code'] == 403
    assert data['message'] == '没有权限编辑此文章'
    
    # 恢复文章作者
    test_post.author = test_user
    db.session.commit()

def test_del_post_success(client, test_token, test_user, monkeypatch):
    """测试成功删除文章"""
    # 创建一个临时文章用于删除测试
    from app import db
    from app.models import Post
    
    post = Post(body='临时文章用于删除测试', author=test_user)
    db.session.add(post)
    db.session.commit()
    
    # 模拟del_qiniu_image函数
    def mock_del_qiniu_image(**kwargs):
        return True
    
    # 应用模拟
    monkeypatch.setattr('app.api.posts.del_qiniu_image', mock_del_qiniu_image)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.delete(f'/api/v1/posts/{post.id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '文章删除成功'
    
    # 验证文章已删除
    deleted_post = Post.query.get(post.id)
    assert deleted_post is None

def test_del_post_with_images(client, test_token, test_user, monkeypatch):
    """测试删除带图片的文章"""
    # 创建一个临时文章和图片用于删除测试
    from app import db
    from app.models import Post, Image
    
    post = Post(body='临时带图片文章', author=test_user, type=PostType.IMAGE)
    db.session.add(post)
    db.session.flush()
    
    image = Image(url='test_delete_image.jpg', type=ImageType.POST, related_id=post.id)
    db.session.add(image)
    db.session.commit()
    
    # 模拟del_qiniu_image函数
    called_with = {}
    def mock_del_qiniu_image(**kwargs):
        called_with.update(kwargs)
        return True
    
    # 应用模拟
    monkeypatch.setattr('app.api.posts.del_qiniu_image', mock_del_qiniu_image)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.delete(f'/api/v1/posts/{post.id}', headers=headers)
    assert response.status_code == 200
    
    # 验证文章和图片已删除
    deleted_post = Post.query.get(post.id)
    assert deleted_post is None
    
    deleted_image = Image.query.filter_by(related_id=post.id).first()
    assert deleted_image is None
    
    # 验证调用了del_qiniu_image函数
    assert 'keys' in called_with
    assert called_with['keys'] == ['test_delete_image.jpg']

def test_del_post_not_found(client, test_token):
    """测试删除不存在的文章"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.delete('/api/v1/posts/999', headers=headers)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['code'] == 404
    assert data['message'] == '文章不存在'

def test_del_post_unauthorized(client, test_post):
    """测试未授权删除文章"""
    response = client.delete(f'/api/v1/posts/{test_post.id}')
    assert response.status_code == 401