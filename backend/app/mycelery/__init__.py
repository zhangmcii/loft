from celery import Celery, Task


def celery_init_app(app) -> Celery:
    """
    启动目录(mac环境)：  cd blog_backend
    mac: celery -A app.make_celery worker --loglevel INFO

    windows: celery -A app.make_celery worker --loglevel INFO -P eventlet

    启动beat调度器:
    celery -A app.make_celery beat --loglevel INFO
    """

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(
        app.name, task_cls=FlaskTask, BROKER_CONNECTION_RETRY_ON_STARTUP=True
    )
    celery_app.config_from_object(app.config["CELERY"])

    # 配置周期性任务
    celery_app.conf.beat_schedule = {
        "hello_world_task": {
            "task": "app.mycelery.tasks.hello_world",
            "schedule": 30.0,
        },
        "del_post_task": {
            "task": "app.mycelery.tasks.hard_delete",
            "schedule": 60.0 * 2,
        },
    }

    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
