import os

from app import create_app

flask_app = create_app(os.getenv("FLASK_CONFIG") or "default")
celery_app = flask_app.extensions["celery"]
