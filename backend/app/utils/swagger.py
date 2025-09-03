"""
API文档配置模块
"""
from flasgger import Swagger


def setup_swagger(app):
    """
    配置Swagger UI

    Args:
        app: Flask应用实例
    """
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,  # 所有接口
                "model_filter": lambda tag: True,  # 所有模型
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
    }

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Flask API",
            "description": "Flask API 接口文档",
            "version": "1.0.0",
            "contact": {"name": "API Support", "email": "support@example.com"},
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"',
            }
        },
        "security": [{"Bearer": []}],
    }

    Swagger(app, config=swagger_config, template=swagger_template)
