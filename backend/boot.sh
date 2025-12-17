#!/bin/sh
source venv/bin/activate

# 确保logs目录存在
mkdir -p logs

# 转为utf-8
while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        echo Deploy success
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

# 启动 Celery worker 和 beat
celery -A app.make_celery worker --loglevel INFO -P eventlet --logfile=logs/celery_worker.log &
CELERY_WORKER_PID=$!

celery -A app.make_celery beat --loglevel INFO --logfile=logs/celery_beat.log --schedule=logs/celerybeat-schedule &
CELERY_BEAT_PID=$!

# 主应用服务
gunicorn -b :5000 -w 8 --access-logfile - --error-logfile - flasky:app &
MAIN_APP_PID=$!

# 等待主应用启动
sleep 3

# WebSocket 服务
gunicorn -b :5001 -w 1 --worker-class eventlet --access-logfile - --error-logfile - flasky_socketio:app &
WEBSOCKET_PID=$!

# 等待任意子进程退出
wait -n $CELERY_WORKER_PID $CELERY_BEAT_PID $MAIN_APP_PID $WEBSOCKET_PID

echo "进程异常退出，退出码：$?"