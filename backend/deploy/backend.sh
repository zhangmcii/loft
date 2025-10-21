#!/bin/bash

function backend_to_remote() {
    backend_tar="flasky_backend.tar"
    if [[ -e  $backend_tar ]];then
      rm -f $backend_tar
      echo "已删除 $backend_tar"
    fi

    # 构建镜像并保存为tar文件
    if sysctl -n machdep.cpu.brand_string | grep -q "Apple"; then
      # mac芯片为M4，指定平台为 linux/amd64
      docker build --platform linux/amd64 -t nizhenshi/flasky_backend ./backend
    else
      docker build -t nizhenshi/flasky_backend ./backend
    fi
    docker save -o flasky_backend.tar nizhenshi/flasky_backend

    # 传输tar文件到远程服务器
    LOCAL_FILE=$backend_tar
    REMOTE_FILE="/home/ubuntu/user/"
    scp $LOCAL_FILE $ROMOTE_USER@$ROMOTE_HOST:$REMOTE_FILE
    if [[ $? -eq 0 ]];then
      echo "传输成功 $LOCAL_FILE"
    else
      echo "传输失败"
    fi
    if [[ -e  $backend_tar ]];then
      rm -f $backend_tar
      echo "已删除 $backend_tar"
    fi

    # 远程运行容器命令
    remote_cmd_backend="docker rm -f flasky_backend;docker rmi nizhenshi/flasky_backend;docker load -i flasky_backend.tar;docker run --name flasky_backend -v /var/log/loft:/home/flasky/logs -d -p 4289:5000 --network database_n -e FLASK_CONFIG=docker  -e DATABASE_URL=mysql+pymysql://flasky:1234@mysql/flasky -e MAIL_USERNAME=zmc_li@foxmail.com -e MAIL_PASSWORD=idycznxncyvhdeef -e REDIS_URL=redis://:1234@myredis:6379/0  -e REDIS_HOST=myredis -e QINIU_ACCESS_KEY=PpQuM1ZtcXQFQRDnDgvVBRhw2NBu8Ew3ZE-izAPW -e QINIU_SECRET_KEY=BbyCwZuZZxtpBb1QtZuTA7syKd-JlZPatjK7hcfv -e QINIU_BUCKET_NAME=b-article-2 -e QINIU_DOMAIN=http://qn.191718.com nizhenshi/flasky_backend:latest;"
    echo "remote_cmd_backend:" $remote_cmd_backend
    ssh $ROMOTE_USER@$ROMOTE_HOST "cd $REMOTE_FILE;$remote_cmd_backend"
    if [[ $? -eq 0 ]];then
      echo "执行成功"
    else
      echo "执行失败"
    fi
}

