import pytest
from app import create_app, db
from app.models import Role


@pytest.fixture
def app():
    """创建并配置一个Flask应用实例用于测试

    每个测试函数都会获得一个新的应用实例和数据库
    """
    app = create_app("testing")

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


@pytest.fixture
def flask_app_context(app):
    """提供应用上下文的夹具"""
    with app.app_context():
        yield


@pytest.fixture
def flask_pre_and_post_process(app):
    """每个测试前后处理数据库的夹具"""
    # 测试前的处理已经在app夹具中完成
    yield
    # 测试后的清理也在app夹具中完成


class AuthAction:
    def __init__(self, client):
        self._client = client
        self._token = None

    def register(self, username="test", password="test"):
        return self._client.post(
            "/auth/register",
            json={
                "username": username,
                "password": password,
            },
        )

    def register_admin(self, username="admin", password="admin"):
        return self._client.post(
            "/auth/register",
            json={
                "email": "zmc_li@foxmail.com",
                "username": username,
                "password": password,
            },
        )

    def login(self, username="test", password="test"):
        r = self._client.post(
            "/auth/login",
            json={
                "uiAccountName": username,
                "uiPassword": password,
            },
        )
        self._token = r.json.get("token")
        return r

    def get_headers(self):
        return {
            "Authorization": self._token,
            "Accept": "application/json",
            "Content-type": "application/json",
        }


@pytest.fixture
def auth(client):
    """提供认证操作的夹具"""
    return AuthAction(client)
