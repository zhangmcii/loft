import pytest
import json
from flask import url_for
from app.models import Tag

def test_get_all_tags(client):
    """测试获取所有标签"""
    # 创建测试标签
    from app import db
    tag1 = Tag(name='测试标签1')
    tag2 = Tag(name='测试标签2')
    db.session.add_all([tag1, tag2])
    db.session.commit()
    
    response = client.get('/tags_list')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert '测试标签1' in data['data']
    assert '测试标签2' in data['data']
    
    # 清理测试数据
    Tag.query.filter(Tag.name.in_(['测试标签1', '测试标签2'])).delete(synchronize_session=False)
    db.session.commit()

def test_edit_user_tag_success(client, test_token, test_user):
    """测试成功更新用户标签"""
    # 创建测试标签
    from app import db
    tag = Tag(name='已有标签')
    db.session.add(tag)
    db.session.commit()
    
    headers = {
        'Authorization': f'Bearer {test_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'tagAdd': ['新标签', '已有标签'],
        'tagRemove': []
    }
    response = client.post('/update_user_tag', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '用户标签更新成功'
    
    # 验证用户标签已更新
    user_tags = [tag.name for tag in test_user.tags]
    assert '新标签' in user_tags
    assert '已有标签' in user_tags
    
    # 测试移除标签
    data = {
        'tagAdd': [],
        'tagRemove': ['新标签']
    }
    response = client.post('/update_user_tag', headers=headers, json=data)
    assert response.status_code == 200
    
    # 验证标签已移除
    user_tags = [tag.name for tag in test_user.tags]
    assert '新标签' not in user_tags
    assert '已有标签' in user_tags
    
    # 清理测试数据
    test_user.tags = []
    Tag.query.filter(Tag.name.in_(['新标签', '已有标签'])).delete(synchronize_session=False)
    db.session.commit()

def test_edit_user_tag_unauthorized(client):
    """测试未授权更新用户标签"""
    data = {
        'tagAdd': ['未授权标签'],
        'tagRemove': []
    }
    response = client.post('/update_user_tag', json=data)
    assert response.status_code == 401
    
    # 验证标签未创建
    tag = Tag.query.filter_by(name='未授权标签').first()
    assert tag is None

def test_update_tag_success(client):
    """测试成功更新公共标签库"""
    data = {
        'tagAdd': ['公共标签1', '公共标签2'],
        'tagRemove': []
    }
    response = client.post('/update_tag', json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '公共标签库更新成功'
    
    # 验证标签已创建
    tags = Tag.query.filter(Tag.name.in_(['公共标签1', '公共标签2'])).all()
    assert len(tags) == 2
    
    # 测试移除标签
    data = {
        'tagAdd': [],
        'tagRemove': ['公共标签1']
    }
    response = client.post('/update_tag', json=data)
    assert response.status_code == 200
    
    # 验证标签已移除
    tag = Tag.query.filter_by(name='公共标签1').first()
    assert tag is None
    tag = Tag.query.filter_by(name='公共标签2').first()
    assert tag is not None
    
    # 清理测试数据
    Tag.query.filter_by(name='公共标签2').delete()
    from app import db
    db.session.commit()

def test_update_tag_empty_lists(client):
    """测试使用空列表更新公共标签库"""
    data = {
        'tagAdd': [],
        'tagRemove': []
    }
    response = client.post('/update_tag', json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '公共标签库更新成功'