#!/bin/bash


#------------------------------------------------------------------------------
# 基础配置
#------------------------------------------------------------------------------
PROJECT_NAME="flasky"

REMOTE_USER="root"
REMOTE_HOST="your.server.ip"
REMOTE_WORK_DIR="/root/user"

DOCKER_NETWORK="database_n"

#------------------------------------------------------------------------------
# 前端配置
#------------------------------------------------------------------------------
FRONTEND_BUILD_MODE="production"
FRONTEND_BUILD_DIR="dist"
FRONTEND_NGINX_DIR="/usr/local/nginx/html"

#------------------------------------------------------------------------------
# 后端配置
#------------------------------------------------------------------------------
BACKEND_HOST_PORT="4289"
BACKEND_CONTAINER_PORT="5000"

LOG_MOUNT_PATH="/var/log/loft"
CONTAINER_LOG_PATH="/home/flasky/logs"

BACKEND_IMAGE_NAME="${PROJECT_NAME}_backend"
BACKEND_CONTAINER_NAME="${PROJECT_NAME}_backend"

#------------------------------------------------------------------------------
# MySQL 配置
#------------------------------------------------------------------------------
MYSQL_IMAGE="mysql/mysql-server:latest"
MYSQL_CONTAINER_NAME="mysql"

MYSQL_ROOT_PASSWORD="root1234"
MYSQL_DATABASE="flasky"
MYSQL_USER="flasky"
MYSQL_PASSWORD="1234"
MYSQL_DATA_VOLUME="mysql_data"

#------------------------------------------------------------------------------
# Redis 配置
#------------------------------------------------------------------------------
REDIS_IMAGE="redis:latest"
REDIS_CONTAINER_NAME="myredis"
REDIS_PASSWORD="redis1234"
REDIS_DATA_VOLUME="redis_data"
REDIS_CONFIG_PATH="/root/user/blog/redis.conf"

#------------------------------------------------------------------------------
# 环境变量（后端应用）
#------------------------------------------------------------------------------
FLASK_CONFIG="docker"
DATABASE_URL="mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_CONTAINER_NAME}/${MYSQL_DATABASE}"
REDIS_URL="redis://:${REDIS_PASSWORD}@${REDIS_CONTAINER_NAME}:6379/0"
REDIS_HOST="${REDIS_CONTAINER_NAME}"

# 邮件服务（如需使用请修改）
MAIL_USERNAME="your_email@example.com"
MAIL_PASSWORD="your_mail_password"

# 七牛云（可选，如不使用留空）
QINIU_ACCESS_KEY=""
QINIU_SECRET_KEY=""
QINIU_BUCKET_NAME=""
QINIU_DOMAIN=""

#==============================================================================
# 工具函数
#==============================================================================
print_info()    { echo -e "\033[32m[INFO]\033[0m $1"; }
print_error()   { echo -e "\033[31m[ERROR]\033[0m $1"; }
print_warning() { echo -e "\033[33m[WARNING]\033[0m $1"; }

# 检查依赖工具
check_dependencies() {
    for cmd in docker ssh scp npm; do
        if ! command -v $cmd &>/dev/null; then
            print_error "缺少依赖: $cmd"
            exit 1
        fi
    done
    print_info "依赖检查通过"
}

#==============================================================================
# 部署前端
#==============================================================================
deploy_frontend() {
    print_info "开始部署前端..."

    local base_path=$(pwd)/frontend
    if [[ ! -d "$base_path" ]]; then
        print_error "前端目录不存在: $base_path"
        return 1
    fi

    cd "$base_path" || return 1
    print_info "构建前端..."
    npm run build --mode="$FRONTEND_BUILD_MODE" || { print_error "前端构建失败"; return 1; }

    [[ ! -d "$FRONTEND_BUILD_DIR" ]] && { print_error "构建目录不存在: $FRONTEND_BUILD_DIR"; return 1; }

    print_info "压缩构建文件..."
    tar -czf dist.tar.gz -C "$FRONTEND_BUILD_DIR" .

    print_info "清理远程 Nginx 目录..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "find $FRONTEND_NGINX_DIR -mindepth 1 -delete"

    print_info "传输前端文件..."
    scp dist.tar.gz "$REMOTE_USER@$REMOTE_HOST:$FRONTEND_NGINX_DIR"

    print_info "远程解压并重启 Nginx..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        cd $FRONTEND_NGINX_DIR &&
        tar -xzf dist.tar.gz -C . --no-xattrs &&
        rm dist.tar.gz &&
        nginx -s reload || true
    "

    rm -f dist.tar.gz
    print_info "前端部署完成"
}

#==============================================================================
# 部署后端
#==============================================================================
deploy_backend() {
    print_info "开始部署后端..."

    local backend_tar="${BACKEND_IMAGE_NAME}.tar"

    [[ -e "$backend_tar" ]] && rm -f "$backend_tar"

    [[ ! -d "backend" ]] && { print_error "后端目录不存在"; return 1; }

    print_info "构建后端 Docker 镜像..."
    docker build -t "$BACKEND_IMAGE_NAME" ./backend || { print_error "镜像构建失败"; return 1; }

    print_info "保存镜像为 tar..."
    docker save -o "$backend_tar" "$BACKEND_IMAGE_NAME"

    print_info "传输镜像文件到远程服务器..."
    scp "$backend_tar" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_WORK_DIR/"

    rm -f "$backend_tar"

    print_info "远程加载镜像并运行容器..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        set -e
        cd $REMOTE_WORK_DIR

        docker rm -f $BACKEND_CONTAINER_NAME 2>/dev/null || true
        docker load -i $backend_tar
        rm -f $backend_tar

        docker run -d --name $BACKEND_CONTAINER_NAME \
            --restart unless-stopped \
            --network $DOCKER_NETWORK \
            -v $LOG_MOUNT_PATH:$CONTAINER_LOG_PATH \
            -p $BACKEND_HOST_PORT:$BACKEND_CONTAINER_PORT \
            -e FLASK_CONFIG=$FLASK_CONFIG \
            -e DATABASE_URL='$DATABASE_URL' \
            -e MAIL_USERNAME=$MAIL_USERNAME \
            -e MAIL_PASSWORD=$MAIL_PASSWORD \
            -e REDIS_URL='$REDIS_URL' \
            -e REDIS_HOST=$REDIS_HOST \
            -e QINIU_ACCESS_KEY=$QINIU_ACCESS_KEY \
            -e QINIU_SECRET_KEY=$QINIU_SECRET_KEY \
            -e QINIU_BUCKET_NAME=$QINIU_BUCKET_NAME \
            -e QINIU_DOMAIN=$QINIU_DOMAIN \
            $BACKEND_IMAGE_NAME:latest
    "

    print_info "后端部署完成"
}

#==============================================================================
# 初始化 MySQL + Redis
#==============================================================================
create_redis_config() {
    print_info "在远程服务器创建 Redis 配置文件..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        mkdir -p $(dirname $REDIS_CONFIG_PATH) &&
        cat > $REDIS_CONFIG_PATH <<EOF
bind 0.0.0.0
port 6379
requirepass $REDIS_PASSWORD
appendonly yes
appendfsync everysec
save 900 1
save 300 10
save 60 10000
maxmemory-policy allkeys-lru
tcp-keepalive 300
timeout 0
EOF
    "
}

init_services() {
    print_info "初始化数据库和缓存服务..."

    docker pull "$MYSQL_IMAGE" || return 1
    docker pull "$REDIS_IMAGE" || return 1

    docker save -o mysql.tar "$MYSQL_IMAGE"
    docker save -o redis.tar "$REDIS_IMAGE"

    scp mysql.tar redis.tar "$REMOTE_USER@$REMOTE_HOST:$REMOTE_WORK_DIR/"
    rm -f mysql.tar redis.tar

    ssh "$REMOTE_USER@$REMOTE_HOST" "
        docker network ls | grep -q $DOCKER_NETWORK || docker network create $DOCKER_NETWORK
    "

    create_redis_config

    ssh "$REMOTE_USER@$REMOTE_HOST" "
        set -e
        cd $REMOTE_WORK_DIR

        docker load -i mysql.tar
        docker load -i redis.tar
        rm -f mysql.tar redis.tar

        docker rm -f $MYSQL_CONTAINER_NAME $REDIS_CONTAINER_NAME 2>/dev/null || true
        docker volume create $MYSQL_DATA_VOLUME >/dev/null || true
        docker volume create $REDIS_DATA_VOLUME >/dev/null || true

        docker run -d --name $MYSQL_CONTAINER_NAME \
            --restart unless-stopped \
            --network $DOCKER_NETWORK --network-alias $MYSQL_CONTAINER_NAME \
            -v $MYSQL_DATA_VOLUME:/var/lib/mysql \
            -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
            -e MYSQL_DATABASE=$MYSQL_DATABASE \
            -e MYSQL_USER=$MYSQL_USER \
            -e MYSQL_PASSWORD=$MYSQL_PASSWORD \
            $MYSQL_IMAGE

        docker run -d --name $REDIS_CONTAINER_NAME \
            --restart unless-stopped \
            --network $DOCKER_NETWORK --network-alias $REDIS_CONTAINER_NAME \
            -v $REDIS_CONFIG_PATH:/usr/local/etc/redis/redis.conf \
            -v $REDIS_DATA_VOLUME:/data \
            $REDIS_IMAGE \
            redis-server /usr/local/etc/redis/redis.conf --save 60 1 --loglevel warning
    "

    print_info "MySQL 和 Redis 初始化完成"
}

#==============================================================================
# 完整初始化部署
#==============================================================================
init_deploy() {
    print_info "开始完整初始化部署..."

    if init_services && deploy_frontend && deploy_backend; then
        print_info "🎉 初始化部署成功"
        echo "--------------------------------------------"
        echo " MySQL 容器:   $MYSQL_CONTAINER_NAME"
        echo " Redis 容器:   $REDIS_CONTAINER_NAME"
        echo " 前端地址:     http://$REMOTE_HOST"
        echo " 后端地址:     http://$REMOTE_HOST:$BACKEND_HOST_PORT"
        echo "--------------------------------------------"
    else
        print_error "初始化部署失败，请检查日志"
        exit 1
    fi
}

#==============================================================================
# 主入口
#==============================================================================
show_help() {
    echo "用法: $0 [选项]"
    echo "  init        初始化部署（数据库 + 缓存 + 应用）"
    echo "  services    仅初始化数据库和缓存服务"
    echo "  frontend    仅部署前端"
    echo "  backend     仅部署后端"
    echo "  all         部署前端和后端"
    echo "  help        显示帮助"
}

main() {
    check_dependencies
    case "${1:-all}" in
        init)       init_deploy ;;
        services)   init_services ;;
        frontend)   deploy_frontend ;;
        backend)    deploy_backend ;;
        all)        deploy_frontend && deploy_backend ;;
        help|-h|--help) show_help ;;
        *) print_error "未知选项: $1"; show_help; exit 1 ;;
    esac
}

main "$@"
