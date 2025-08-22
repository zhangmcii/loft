import pytest
import json
from app.models import Log

def test_logs_admin_access(client, admin_token):
    """测试管理员获取系统日志"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/logs', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert 'data' in data
    assert 'total' in data['extra']

def test_logs_unauthorized(client):
    """测试未授权访问系统日志"""
    response = client.get('/logs')
    assert response.status_code == 401

def test_logs_non_admin(client, test_token):
    """测试非管理员访问系统日志"""
    headers = {'Authorization': f'Bearer {test_token}'}
    response = client.get('/logs', headers=headers)
    assert response.status_code == 403

def test_logs_pagination(client, admin_token):
    """测试系统日志分页"""
    # 创建多个测试日志
    from app import db
    from app.models import Log
    
    # 创建10个测试日志
    for i in range(10):
        log = Log(
            operate_type=f'测试操作{i}',
            operate_user='测试用户',
            operate_content=f'测试内容{i}'
        )
        db.session.add(log)
    db.session.commit()
    
    # 测试第一页
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/logs?page=1&per_page=5', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) == 5
    
    # 测试第二页
    response = client.get('/logs?page=2&per_page=5', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert len(data['data']) > 0
    
    # 清理测试数据
    Log.query.filter(Log.operate_type.like('测试操作%')).delete()
    db.session.commit()

def test_delete_log_success(client, admin_token):
    """测试成功删除系统日志"""
    # 创建测试日志
    from app import db
    from app.models import Log
    
    log1 = Log(operate_type='测试删除操作1', operate_user='测试用户', operate_content='测试内容1')
    log2 = Log(operate_type='测试删除操作2', operate_user='测试用户', operate_content='测试内容2')
    db.session.add_all([log1, log2])
    db.session.commit()
    
    # 删除日志
    headers = {'Authorization': f'Bearer {admin_token}'}
    data = {
        'ids': [log1.id, log2.id]
    }
    response = client.post('/deleteLog', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '日志删除成功'
    
    # 验证日志已删除
    deleted_logs = Log.query.filter(Log.id.in_([log1.id, log2.id])).all()
    assert len(deleted_logs) == 0

def test_delete_log_empty_ids(client, admin_token):
    """测试删除系统日志 - 空ID列表"""
    headers = {'Authorization': f'Bearer {admin_token}'}
    data = {
        'ids': []
    }
    response = client.post('/deleteLog', headers=headers, json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['code'] == 200
    assert data['message'] == '没有提供要删除的日志ID'

def test_delete_log_unauthorized(client):
    """测试未授权删除系统日志"""
    data = {
        'ids': [1, 2]
    }
    response = client.post('/deleteLog', json=data)
    assert response.status_code == 401

def test_delete_log_non_admin(client, test_token):
    """测试非管理员删除系统日志"""
    headers = {'Authorization': f'Bearer {test_token}'}
    data = {
        'ids': [1, 2]
    }
    response = client.post('/deleteLog', headers=headers, json=data)
    assert response.status_code == 403