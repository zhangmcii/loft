FROM python:3.12-alpine

ENV TZ="Asia/Shanghai"

RUN adduser -D flasky
USER flasky

WORKDIR /home/flasky

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY flasky.py config.py boot.sh flasky_socketio.py ./


# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
