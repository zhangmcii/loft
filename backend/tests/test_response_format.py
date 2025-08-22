import pytest
import json
from app import create_app, db
from app.models import User, Role
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    """创建并配置一个Flask应用实例用于测试"""
    app = create_app('testing')
    
    # 创建应用上下文
    with app.app_context():
        db.create_all()
        Role.insert_roles()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建测试命令行运行器"""
    return app.test_cli_runner()


class TestResponseFormat:
    """测试统一接口返回格式"""

    def test_get_user_response_format(self, client):
        """测试获取用户信息的接口返回格式"""
        # 创建一个测试用户
        user = User(email='test@example.com', username='test', password='test')
        db.session.add(user)
        db.session.commit()
        
        # 请求用户信息
        response = client.get(f'/api/v1/users/{user.id}')
        
        # 检查响应状态码
        assert response.status_code == 200
        
        # 检查响应格式
        data = json.loads(response.data)
        assert 'code' in data
        assert 'message' in data
        assert 'data' in data
        
        # 检查状态码
        assert data['code'] == 200
        
        # 检查消息
        assert data['message'] == 'success'
        
        # 检查数据
        assert data['data'] is not None
        assert 'username' in data['data']
        assert data['data']['username'] == 'test'

    def test_user_not_found_response_format(self, client):
        """测试用户不存在时的接口返回格式"""
        # 请求不存在的用户
        response = client.get('/api/v1/users/999')
        
        # 检查响应状态码
        assert response.status_code == 404
        
        # 检查响应格式
        data = json.loads(response.data)
        assert 'code' in data
        assert 'message' in data
        assert 'data' in data
        
        # 检查状态码
        assert data['code'] == 404
        
        # 检查数据
        assert data['data'] == {}

    def test_search_followed_response_format(self, client):
        """测试搜索关注用户的接口返回格式"""
        # 注册一个测试用户并登录
        auth_response = client.post('/auth/register', json={
            'username': 'test',
            'password': 'test'
        })
        result = json.loads(auth_response.data)
        assert result.get('message') == 'success'
        
        # 获取JWT令牌
        auth_response = client.post('/auth/login', json={
            'uiAccountName': 'test',
            'uiPassword': 'test'
        })
        
        token = json.loads(auth_response.data).get('token')
        assert token is not None, f"登录失败，返回内容：{auth_response.data}"
        headers = {'Authorization': token}
        
        # 请求搜索关注用户
        response = client.get('/api/v1/search_followed?name=test', headers=headers)
        
        # 检查响应格式
        data = json.loads(response.data)
        assert 'code' in data
        assert 'message' in data
        assert 'data' in data
        
        # 检查状态码
        assert data['code'] == 200
        
        # 检查消息
        assert data['message'] == 'success'
        
        # 检查数据
        assert isinstance(data['data'], list)