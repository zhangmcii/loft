import pytest
from app import create_app, db
from app.models import Role, User


# @pytest.fixture(scope='module')
# def app():
#     app = create_app('testing')
#     return app
#
#
# @pytest.fixture
# def client(app):
#     return app.test_client()

@pytest.fixture(scope='module')
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
    return app.test_cli_runner()


class Test_pre_post_process:
    def pre_process(self, client):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def post_process(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


@pytest.fixture
def flask_pre_and_post_process(client):
    t = Test_pre_post_process()
    t.pre_process(client)
    yield
    t.post_process()


class AuthAction:
    def __init__(self, client):
        self._client = client

    def register(self, username='test', password = 'test'):
        return self._client.post('/auth/register', json={
        'email': 'zmc_li@foxmail.com',
        'username': username,
        'password': password,
    })

    def login(self, username='test', password = 'test'):

        r = self._client.post('/auth/login', json={
            'uiAccountName': username,
            'uiPassword': password,
        })
        self._token = r.json.get('token')
        return r

    def get_headers(self):
        return {
            'Authorization': self._token,
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }

@pytest.fixture
def auth(client):
    return AuthAction(client)
