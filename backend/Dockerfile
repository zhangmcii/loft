FROM python:3.12-alpine

ENV FLASK_APP=flasky.py
ENV FLASK_CONFIG=docker
ENV TZ="Asia/Shanghai"

ENV QQ_CLIENT_ID=102827468
ENV QQ_CLIENT_SECRET=d9XiqpfLuLYcYN6g

ENV WEIBO_CLIENT_ID=1701597640
ENV WEIBO_CLIENT_SECRET=ce7a05c99cf72ec293efa69ede797641
ENV WEIBO_REDIRECT_URI=https://191718.com/auth/oauth/callback/weibo

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
