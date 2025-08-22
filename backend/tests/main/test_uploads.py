import pytest
import json
import os
import time
from flask import url_for
from app.models import Image, ImageType

def test_get_upload_token(client, monkeypatch):
    """测试获取七牛云上传凭证"""
    # 模拟Auth类的upload_token方法
    def mock_upload_token(bucket_name, key=None, expires=3600, policy=None, strict_policy=True):
        return 'fake_upload_token'
    
    # 应用模拟
    monkeypatch.setattr('app.main.uploads.q.upload_token', mock_upload_token)
    
    response = client.get('/get_upload_token')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['data']['upload_token'] == 'fake_upload_token'

def test_get_signed_image_urls(client, monkeypatch):
    """测试获取私有存储图片url"""
    # 模拟Auth类的private_download_url方法
    def mock_private_download_url(url, expires=3600):
        return f'signed_{url}'
    
    # 应用模拟
    monkeypatch.setattr('app.main.uploads.q.private_download_url', mock_private_download_url)
    monkeypatch.setattr('os.getenv', lambda key, default=None: 'http://example.com' if key == 'QINIU_DOMAIN' else default)
    
    data = {
        'keys': ['image1.jpg', 'image2.jpg']
    }
    response = client.post('/get_signed_image_urls', json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']['signed_urls']) == 2
    assert 'signed_' in data['data']['signed_urls'][0]

def test_get_signed_image_urls_missing_keys(client):
    """测试获取私有存储图片url - 缺少keys参数"""
    data = {}
    response = client.post('/get_signed_image_urls', json=data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['code'] == 400
    assert 'Missing keys parameter' in data['message']

def test_delete_image(client, test_token, monkeypatch):
    """测试删除七牛云图片"""
    # 模拟build_batch_delete和bucket.batch方法
    def mock_build_batch_delete(bucket_name, keys):
        return [f'delete {bucket_name}:{key}' for key in keys]
    
    def mock_batch(ops):
        return True
    
    # 应用模拟
    monkeypatch.setattr('app.main.uploads.build_batch_delete', mock_build_batch_delete)
    monkeypatch.setattr('app.main.uploads.bucket.batch', mock_batch)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'bucket': 'test_bucket',
        'key': ['image1.jpg', 'image2.jpg']
    }
    response = client.delete('/del_image', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '图片删除成功'

def test_delete_image_unauthorized(client):
    """测试未授权删除七牛云图片"""
    data = {
        'bucket': 'test_bucket',
        'key': ['image1.jpg']
    }
    response = client.delete('/del_image', json=data)
    assert response.status_code == 401

def test_query_qiniu_key(client, monkeypatch):
    """测试查询七牛云某个bucket指定目录的所有文件名"""
    # 模拟bucket.list方法和info.text_body
    class MockInfo:
        def __init__(self):
            self.text_body = json.dumps({
                'items': [
                    {'key': 'userBackground/static/placeholder'},
                    {'key': 'userBackground/static/image1.jpg'},
                    {'key': 'userBackground/static/image2.jpg'},
                    {'key': 'userBackground/static/image3.jpg'},
                    {'key': 'userBackground/static/image4.jpg'},
                    {'key': 'userBackground/static/image5.jpg'},
                    {'key': 'userBackground/static/image6.jpg'},
                    {'key': 'userBackground/static/image7.jpg'}
                ]
            })
    
    def mock_list(bucket_name, prefix, marker, limit, delimiter):
        return None, True, MockInfo()
    
    # 应用模拟
    monkeypatch.setattr('app.main.uploads.bucket.list', mock_list)
    monkeypatch.setattr('app.utils.common.get_avatars_url', lambda key: f'http://example.com/{key}')
    
    # 测试第一页
    response = client.get('/dir_name?currentPage=1&pageSize=3&completeUrl=1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) == 3
    assert 'http://example.com/' in data['data'][0]
    assert data['total'] == 7  # 总数减去placeholder
    
    # 测试第二页
    response = client.get('/dir_name?currentPage=2&pageSize=3&completeUrl=1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) == 3
    
    # 测试不完整URL
    response = client.get('/dir_name?currentPage=1&pageSize=3&completeUrl=0')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert 'http://example.com/' not in data['data'][0]

def test_get_favorite_book_image(client, test_user):
    """测试获取用户兴趣图片"""
    # 创建测试图片
    from app import db
    image = Image(
        url='test_book.jpg',
        type=ImageType.BOOK,
        describe='测试书籍',
        related_id=test_user.id
    )
    db.session.add(image)
    db.session.commit()
    
    response = client.get(f'/user/{test_user.id}/interest_images')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    assert data['data'][0]['url'] is not None
    assert data['data'][0]['type'] == ImageType.BOOK.value
    
    # 清理测试数据
    Image.query.filter_by(id=image.id).delete()
    db.session.commit()

def test_upload_favorite_book_image(client, test_token, test_user, monkeypatch):
    """测试上传兴趣封面"""
    # 模拟del_qiniu_image函数
    def mock_del_qiniu_image(keys, bucket_name=None):
        return True
    
    # 应用模拟
    monkeypatch.setattr('app.main.uploads.del_qiniu_image', mock_del_qiniu_image)
    
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'type': 'book',
        'urls': ['book1.jpg', 'book2.jpg'],
        'names': ['书籍1', '书籍2']
    }
    response = client.post(f'/user/{test_user.id}/interest_images', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) == 2
    
    # 验证图片已创建
    images = Image.query.filter_by(related_id=test_user.id, type=ImageType.BOOK).all()
    assert len(images) == 2
    assert images[0].url == 'book1.jpg'
    assert images[0].describe == '书籍1'
    
    # 测试上传电影封面
    data = {
        'type': 'movie',
        'urls': ['movie1.jpg'],
        'names': ['电影1']
    }
    response = client.post(f'/user/{test_user.id}/interest_images', headers=headers, json=data)
    assert response.status_code == 200
    
    # 验证电影图片已创建
    movie_images = Image.query.filter_by(related_id=test_user.id, type=ImageType.MOVIE).all()
    assert len(movie_images) == 1
    assert movie_images[0].url == 'movie1.jpg'
    assert movie_images[0].describe == '电影1'
    
    # 清理测试数据
    Image.query.filter_by(related_id=test_user.id).delete()
    from app import db
    db.session.commit()

def test_upload_favorite_book_image_unauthorized(client, test_user):
    """测试未授权上传兴趣封面"""
    data = {
        'type': 'book',
        'urls': ['book1.jpg'],
        'names': ['书籍1']
    }
    response = client.post(f'/user/{test_user.id}/interest_images', json=data)
    assert response.status_code == 401
    
    # 验证图片未创建
    images = Image.query.filter_by(related_id=test_user.id, type=ImageType.BOOK).all()
    assert len(images) == 0