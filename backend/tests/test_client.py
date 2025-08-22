import pytest
from app import create_app, db

def test_client():
    assert not create_app('default').testing
    assert create_app('testing').testing


@pytest.mark.usefixtures('flask_pre_and_post_process')
def test_login(client):
    # 注册
    response = client.post('/auth/register', json={
        'email': 'john@example.com',
        'username': 'john',
        'password': 'cat',
    })
    assert response.json.get('message') == 'success'
    
    # 登录
    res = client.post('/auth/login', json={
        'uiAccountName': 'john',
        'uiPassword': 'cat',
    })
    assert res.json.get('message') == 'success'
