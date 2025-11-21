#!/bin/sh
source venv/bin/activate

# 转为utf-8
while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        echo Depoly success
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

celery -A app.make_celery worker --loglevel INFO -P eventlet --logfile=logs/celery_worker.log &
celery -A app.make_celery beat --loglevel INFO --logfile=logs/celery_beat.log --schedule=logs/celerybeat-schedule &
exec gunicorn -b :5000 --worker-class eventlet -w 4 --access-logfile - --error-logfile - flasky:app