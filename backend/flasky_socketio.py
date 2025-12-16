import eventlet

# 打补丁。 Redis 的 Python 客户端（redis-py）依赖原生 socket，若不提前给 eventlet 打猴子补丁，
# 会导致 Redis 连接与 eventlet 异步引擎冲突，触发 RuntimeError。
eventlet.monkey_patch()

import os

from app import create_app, socketio

app = create_app(os.getenv("FLASK_CONFIG") or "default")

if __name__ == "__main__":
    socketio.run(
        app, host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"), port=5001
    )
