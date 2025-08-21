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


class TestApiResponse:
    """测试API接口的统一返回格式"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        
        # 创建测试用户
        self.user = User(email='test@example.com', username='test', password='test')
        db.session.add(self.user)
        db.session.commit()
        
        # 创建测试客户端
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_user_response_format(self):
        """测试获取用户信息的接口返回格式"""
        # 请求用户信息
        response = self.client.get(f'/api/v1/users/{self.user.id}')
        
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
    
    def test_update_user_response_format(self):
        """测试更新用户信息的接口返回格式"""
        # 创建访问令牌
        with self.app.app_context():
            access_token = create_access_token(identity=self.user)
        
        # 更新用户信息
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        response = self.client.post(
            '/api/v1/update_user',
            headers=headers,
            json={'nickname': 'New Name'}
        )
        
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
        assert data['message'] == '用户信息更新成功'
        
        # 检查数据
        assert data['data'] == {}
        
        # 验证用户信息已更新
        updated_user = User.query.get(self.user.id)
        assert updated_user.nickname == 'New Name'