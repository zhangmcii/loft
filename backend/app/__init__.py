import logging
import os

from config import config
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_redis import FlaskRedis
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_caching import Cache

from .mycelery import celery_init_app
from .utils.logger import setup_logging


def my_key_func():
    """根据当前用户id限速"""
    return current_user.id if current_user else get_remote_address


db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
redis = FlaskRedis()
socketio = SocketIO()
limiter = Limiter(
    my_key_func,
    storage_uri=f"redis://:1234@{os.getenv('REDIS_HOST') or os.getenv('FLASK_RUN_HOST')}:6379/3",
)
cache = Cache()


def create_app(config_name):
    app = Flask(__name__)

    # 设置代理配置
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,  # 对应 X-Forwarded-For（信任1层代理）
        x_proto=1,  # 对应 X-Forwarded-Proto（信任1层代理）
        x_host=1,  # 对应 X-Forwarded-Host（信任1层代理）
        x_prefix=1,  # 对应 X-Forwarded-Prefix（信任1层代理）
    )

    # 跨域
    CORS(app)

    # 开发模式执行celery启动命令时，需要加载环境变量
    if not os.getenv("APP_RUN"):
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的路径
        current_dir_path = os.path.dirname(current_file_path)
        # 获取父目录的路径
        parent_dir_path = os.path.dirname(current_dir_path)
        dotenv_path = os.path.join(parent_dir_path, ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

    # 读取配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 配置日志系统
    setup_logging(app)
    logging.info(f"应用启动，环境: {config_name}")

    host = os.getenv("REDIS_HOST") or os.getenv("FLASK_RUN_HOST")
    app.config.from_mapping(
        CELERY=dict(
            broker_url=f"redis://:1234@{host}:6379/1",
            result_backend=f"redis://:1234@{host}:6379/2",
        ),
    )

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    redis.init_app(app, decode_responses=True)
    celery_init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", ping_timeout=30, ping_interval=60)
    limiter.init_app(app)
    cache.init_app(app)

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api/v1")

    @app.route("/test_proxy")
    def test_proxy():
        return {
            "real_ip": request.remote_addr,  # 若生效，会返回客户端真实IP（而非Nginx IP）
            "scheme": request.scheme,  # 若生效，会返回 https（若客户端用HTTPS访问Nginx）
            "host": request.host,  # 若生效，会返回客户端访问的域名（如 example.com）
            "prefix": request.environ.get(
                "HTTP_X_FORWARDED_PREFIX"
            ),  # 若配置，会返回 / 或 /api
        }

    @app.errorhandler(Exception)
    def error_handler(e):
        logging.error(f"全局异常: {str(e)}", exc_info=True)
        if os.environ.get("FLASK_DEBUG", None):
            print(e)
        from .utils.response import server_error

        return server_error(message=str(e))

    return app
