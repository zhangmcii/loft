import pytest
import json
from app.models import Message

def test_get_message_history(client, test_token, test_user, admin_user):
    """测试获取聊天历史记录"""
    # 创建测试消息
    from app import db
    
    # 创建一些测试消息
    message1 = Message(
        content='测试消息1',
        sender=test_user,
        receiver=admin_user
    )
    message2 = Message(
        content='测试消息2',
        sender=admin_user,
        receiver=test_user
    )
    db.session.add_all([message1, message2])
    db.session.commit()
    
    # 测试获取消息
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get(f'/msg?userId={admin_user.id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) == 2
    assert 'total' in data['extra']
    
    # 清理测试数据
    Message.query.filter(Message.content.in_(['测试消息1', '测试消息2'])).delete()
    db.session.commit()

def test_get_message_history_pagination(client, test_token, test_user, admin_user):
    """测试聊天历史分页"""
    # 创建测试消息
    from app import db
    
    # 创建10条测试消息
    messages = []
    for i in range(10):
        if i % 2 == 0:
            message = Message(
                content=f'测试消息{i}',
                sender=test_user,
                receiver=admin_user
            )
        else:
            message = Message(
                content=f'测试消息{i}',
                sender=admin_user,
                receiver=test_user
            )
        messages.append(message)
    db.session.add_all(messages)
    db.session.commit()
    
    # 测试第一页
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get(f'/msg?userId={admin_user.id}&page=1', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    
    # 如果有多页，测试第二页
    if data['extra']['total'] > len(data['data']):
        response = client.get(f'/msg?userId={admin_user.id}&page=2', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
    
    # 清理测试数据
    Message.query.filter(Message.content.like('测试消息%')).delete()
    db.session.commit()

def test_get_message_history_unauthorized(client, admin_user):
    """测试未授权获取聊天历史"""
    response = client.get(f'/msg?userId={admin_user.id}')
    assert response.status_code == 401

def test_mark_messages_read(client, test_token, test_user, admin_user):
    """测试标记消息为已读"""
    # 创建测试消息
    from app import db
    
    # 创建未读消息
    message1 = Message(
        content='未读测试消息1',
        sender=admin_user,
        receiver=test_user,
        is_read=False
    )
    message2 = Message(
        content='未读测试消息2',
        sender=admin_user,
        receiver=test_user,
        is_read=False
    )
    db.session.add_all([message1, message2])
    db.session.commit()
    
    # 标记消息为已读
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'ids': [message1.id, message2.id]
    }
    response = client.post('/msg/read', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '消息已标记为已读'
    
    # 验证消息已标记为已读
    updated_message1 = Message.query.get(message1.id)
    updated_message2 = Message.query.get(message2.id)
    assert updated_message1.is_read is True
    assert updated_message2.is_read is True
    
    # 清理测试数据
    Message.query.filter(Message.content.like('未读测试消息%')).delete()
    db.session.commit()

def test_mark_messages_read_unauthorized(client):
    """测试未授权标记消息为已读"""
    data = {
        'ids': [1, 2]
    }
    response = client.post('/msg/read', json=data)
    assert response.status_code == 401

def test_mark_messages_read_empty_ids(client, test_token):
    """测试标记空消息列表为已读"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'ids': []
    }
    response = client.post('/msg/read', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200