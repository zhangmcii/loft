#!/bin/bash

#==============================================================================
# 通用 Docker 部署脚本配置区域
# 请根据您的项目需求修改以下配置变量
#==============================================================================

#------------------------------------------------------------------------------
# 基础项目配置
#------------------------------------------------------------------------------
# 项目名称（用于镜像和容器命名）
PROJECT_NAME="flasky"

# Docker 镜像配置
DOCKER_REGISTRY_USER="random"  # Docker Hub 用户名或私有仓库地址
BACKEND_IMAGE_NAME="${DOCKER_REGISTRY_USER}/${PROJECT_NAME}_backend"
FRONTEND_IMAGE_NAME="${DOCKER_REGISTRY_USER}/${PROJECT_NAME}_frontend"

# 容器名称
BACKEND_CONTAINER_NAME="${PROJECT_NAME}_backend"
FRONTEND_CONTAINER_NAME="${PROJECT_NAME}_frontend"

#------------------------------------------------------------------------------
# 远程服务器配置
#------------------------------------------------------------------------------
# 远程服务器连接信息
REMOTE_USER="root"                    # 远程服务器用户名
REMOTE_HOST="your.server.ip"          # 远程服务器IP地址或域名
REMOTE_WORK_DIR="/root/user"          # 远程服务器工作目录

#------------------------------------------------------------------------------
# 前端部署配置
#------------------------------------------------------------------------------
# 前端构建配置
FRONTEND_BUILD_MODE="production"      # 构建模式：development/production
FRONTEND_BUILD_DIR="dist"             # 本地构建输出目录
FRONTEND_NGINX_DIR="/usr/local/nginx/html"  # 远程Nginx静态文件目录

#------------------------------------------------------------------------------
# 后端部署配置
#------------------------------------------------------------------------------
# 后端服务端口配置
BACKEND_HOST_PORT="4289"              # 宿主机端口
BACKEND_CONTAINER_PORT="5000"         # 容器内端口

# 数据持久化路径配置
LOG_MOUNT_PATH="/var/log/loft"        # 宿主机日志目录
CONTAINER_LOG_PATH="/home/flasky/logs" # 容器内日志目录

# Docker 网络配置
DOCKER_NETWORK="database_n"           # Docker 网络名称

#------------------------------------------------------------------------------
# 数据库和缓存服务配置（用于 init 初始化）
#------------------------------------------------------------------------------
# MySQL 配置
MYSQL_IMAGE="mysql/mysql-server:latest"   # MySQL 镜像名称
MYSQL_CONTAINER_NAME="mysql"              # MySQL 容器名称
MYSQL_DATABASE="flasky"                   # 数据库名称
MYSQL_USER="flasky"                       # 数据库用户名
MYSQL_PASSWORD="xxx"                     # 数据库密码
MYSQL_DATA_VOLUME="mysql_data"            # MySQL 数据卷名称

# Redis 配置
REDIS_IMAGE="redis:latest"                # Redis 镜像名称
REDIS_CONTAINER_NAME="myredis"            # Redis 容器名称
REDIS_PASSWORD="xxx"                     # Redis 密码
REDIS_DATA_VOLUME="redis_data"            # Redis 数据卷名称
REDIS_CONFIG_PATH="/root/user/blog/redis.conf"  # Redis 配置文件路径

#------------------------------------------------------------------------------
# 环境变量配置（后端应用）
#------------------------------------------------------------------------------
# Flask 应用配置
FLASK_CONFIG="docker"                 # Flask 配置环境

# 数据库配置
DATABASE_URL="mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_CONTAINER_NAME}/${MYSQL_DATABASE}"  # 数据库连接URL

# Redis 配置
REDIS_URL="redis://:${REDIS_PASSWORD}@${REDIS_CONTAINER_NAME}:6379/0"  # Redis 连接URL
REDIS_HOST="${REDIS_CONTAINER_NAME}"      # Redis 主机名

# 邮件服务配置
MAIL_USERNAME="your_email@example.com"    # 邮件服务用户名
MAIL_PASSWORD="your_mail_password"        # 邮件服务密码

# 七牛云存储配置（如不使用可留空）
QINIU_ACCESS_KEY="your_qiniu_access_key"  # 七牛云 Access Key
QINIU_SECRET_KEY="your_qiniu_secret_key"  # 七牛云 Secret Key
QINIU_BUCKET_NAME="your_bucket_name"      # 七牛云存储桶名称
QINIU_DOMAIN="http://your.domain.com"     # 七牛云域名

#==============================================================================
# 部署脚本主体（一般情况下无需修改）
#==============================================================================

# 颜色输出函数
print_info() {
    echo -e "\033[32m[INFO]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

# 检查必要的工具
check_dependencies() {
    print_info "检查依赖工具..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v ssh &> /dev/null; then
        print_error "SSH 未安装，请先安装 SSH 客户端"
        exit 1
    fi
    
    if ! command -v scp &> /dev/null; then
        print_error "SCP 未安装，请先安装 SCP"
        exit 1
    fi
    
    print_info "依赖检查完成"
}

# 前端部署函数
deploy_frontend() {
    print_info "开始部署前端..."
    
    local base_path=$(pwd)/frontend
    print_info "前端项目路径: $base_path"
    
    # 检查前端目录是否存在
    if [[ ! -d "$base_path" ]]; then
        print_error "前端目录不存在: $base_path"
        return 1
    fi
    
    # 进入前端目录并构建
    cd "$base_path" || return 1
    
    print_info "开始构建前端项目..."
    npm run build --mode="$FRONTEND_BUILD_MODE"
    
    if [[ $? -ne 0 ]]; then
        print_error "前端构建失败"
        return 1
    fi
    
    # 检查构建目录是否存在
    if [[ ! -d "$FRONTEND_BUILD_DIR" ]]; then
        print_error "构建目录不存在: $FRONTEND_BUILD_DIR"
        return 1
    fi
    
    # 压缩构建文件
    print_info "压缩构建文件..."
    tar -czf dist.tar.gz -C "$FRONTEND_BUILD_DIR" .
    
    if [[ $? -ne 0 ]]; then
        print_error "文件压缩失败"
        return 1
    fi
    
    # 清理远程目录
    print_info "清理远程目录..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "rm -rf $FRONTEND_NGINX_DIR/*"
    
    if [[ $? -ne 0 ]]; then
        print_error "远程目录清理失败"
        return 1
    fi
    
    # 传输文件
    print_info "传输文件到远程服务器..."
    scp dist.tar.gz "$REMOTE_USER@$REMOTE_HOST:$FRONTEND_NGINX_DIR"
    
    if [[ $? -eq 0 ]]; then
        print_info "文件传输成功"
    else
        print_error "文件传输失败"
        return 1
    fi
    
    # 远程解压和重启服务
    print_info "远程解压文件并重启 Nginx..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        cd $FRONTEND_NGINX_DIR && 
        tar -xzf dist.tar.gz -C . --no-xattrs && 
        rm dist.tar.gz && 
        nginx -s reload
    "
    
    if [[ $? -eq 0 ]]; then
        print_info "远程操作成功"
    else
        print_error "远程操作失败"
        return 1
    fi
    
    # 清理本地文件
    print_info "清理本地临时文件..."
    rm -f dist.tar.gz
    
    print_info "前端部署完成！"
    return 0
}

# 后端部署函数
deploy_backend() {
    print_info "开始部署后端..."
    
    local backend_tar="${PROJECT_NAME}_backend.tar"
    
    # 清理旧的 tar 文件
    if [[ -e "$backend_tar" ]]; then
        rm -f "$backend_tar"
        print_info "已删除旧的镜像文件: $backend_tar"
    fi
    
    # 检查后端目录是否存在
    if [[ ! -d "backend" ]]; then
        print_error "后端目录不存在"
        return 1
    fi
    
    # 构建 Docker 镜像
    print_info "构建 Docker 镜像..."
    if sysctl -n machdep.cpu.brand_string 2>/dev/null | grep -q "Apple"; then
        # macOS Apple 芯片，指定平台为 linux/amd64
        print_info "检测到 Apple 芯片，使用 linux/amd64 平台构建"
        docker build --platform linux/amd64 -t "$BACKEND_IMAGE_NAME" ./backend
    else
        docker build -t "$BACKEND_IMAGE_NAME" ./backend
    fi
    
    if [[ $? -ne 0 ]]; then
        print_error "Docker 镜像构建失败"
        return 1
    fi
    
    # 保存镜像为 tar 文件
    print_info "保存镜像为 tar 文件..."
    docker save -o "$backend_tar" "$BACKEND_IMAGE_NAME"
    
    if [[ $? -ne 0 ]]; then
        print_error "镜像保存失败"
        return 1
    fi
    
    # 传输 tar 文件到远程服务器
    print_info "传输镜像文件到远程服务器..."
    scp "$backend_tar" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_WORK_DIR/"
    
    if [[ $? -eq 0 ]]; then
        print_info "镜像文件传输成功"
    else
        print_error "镜像文件传输失败"
        return 1
    fi
    
    # 清理本地 tar 文件
    if [[ -e "$backend_tar" ]]; then
        rm -f "$backend_tar"
        print_info "已删除本地镜像文件: $backend_tar"
    fi
    
    # 构建远程执行命令
    local remote_cmd="
        docker rm -f $BACKEND_CONTAINER_NAME;
        docker rmi $BACKEND_IMAGE_NAME;
        docker load -i $backend_tar;
        docker run --name $BACKEND_CONTAINER_NAME \
            -v $LOG_MOUNT_PATH:$CONTAINER_LOG_PATH \
            -d -p $BACKEND_HOST_PORT:$BACKEND_CONTAINER_PORT \
            --network $DOCKER_NETWORK \
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
            $BACKEND_IMAGE_NAME:latest;
        rm $backend_tar;
    "
    
    # 远程执行部署命令
    print_info "远程执行部署命令..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_WORK_DIR && $remote_cmd"
    
    if [[ $? -eq 0 ]]; then
        print_info "后端部署成功"
    else
        print_error "后端部署失败"
        return 1
    fi
    
    print_info "后端部署完成！"
    return 0
}

# 完整部署函数
deploy_all() {
    print_info "开始完整部署..."
    
    if deploy_frontend && deploy_backend; then
        print_info "🎉 完整部署成功！"
        print_info "前端访问地址: http://$REMOTE_HOST"
        print_info "后端访问地址: http://$REMOTE_HOST:$BACKEND_HOST_PORT"
    else
        print_error "部署过程中出现错误"
        exit 1
    fi
}

# 创建 Redis 配置文件
create_redis_config() {
    print_info "创建 Redis 配置文件..."
    
    local redis_config_content="# Redis 配置文件
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
timeout 0"
    
    # 在远程服务器创建配置文件
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        mkdir -p $(dirname $REDIS_CONFIG_PATH) && 
        cat > $REDIS_CONFIG_PATH << 'EOF'
$redis_config_content
EOF
    "
    
    if [[ $? -eq 0 ]]; then
        print_info "Redis 配置文件创建成功"
        return 0
    else
        print_error "Redis 配置文件创建失败"
        return 1
    fi
}

# 初始化数据库和缓存服务
init_services() {
    print_info "开始初始化数据库和缓存服务..."
    
    # 1. 拉取镜像
    print_info "拉取 MySQL 镜像..."
    docker pull "$MYSQL_IMAGE"
    if [[ $? -ne 0 ]]; then
        print_error "MySQL 镜像拉取失败"
        return 1
    fi
    
    print_info "拉取 Redis 镜像..."
    docker pull "$REDIS_IMAGE"
    if [[ $? -ne 0 ]]; then
        print_error "Redis 镜像拉取失败"
        return 1
    fi
    
    # 2. 导出镜像为 tar 文件
    print_info "导出 MySQL 镜像..."
    docker save -o mysql.tar "$MYSQL_IMAGE"
    if [[ $? -ne 0 ]]; then
        print_error "MySQL 镜像导出失败"
        return 1
    fi
    
    print_info "导出 Redis 镜像..."
    docker save -o redis.tar "$REDIS_IMAGE"
    if [[ $? -ne 0 ]]; then
        print_error "Redis 镜像导出失败"
        return 1
    fi
    
    # 3. 传输镜像文件到远程服务器
    print_info "传输 MySQL 镜像到远程服务器..."
    scp mysql.tar "$REMOTE_USER@$REMOTE_HOST:$REMOTE_WORK_DIR/"
    if [[ $? -ne 0 ]]; then
        print_error "MySQL 镜像传输失败"
        return 1
    fi
    
    print_info "传输 Redis 镜像到远程服务器..."
    scp redis.tar "$REMOTE_USER@$REMOTE_HOST:$REMOTE_WORK_DIR/"
    if [[ $? -ne 0 ]]; then
        print_error "Redis 镜像传输失败"
        return 1
    fi
    
    # 4. 清理本地镜像文件
    print_info "清理本地镜像文件..."
    rm -f mysql.tar redis.tar
    
    # 5. 创建 Docker 网络（如果不存在）
    print_info "创建 Docker 网络..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        docker network ls | grep -q $DOCKER_NETWORK || docker network create $DOCKER_NETWORK
    "
    
    # 6. 创建 Redis 配置文件
    create_redis_config
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    # 7. 在远程服务器导入镜像并运行容器
    print_info "在远程服务器导入镜像并启动服务..."
    
    local remote_init_cmd="
        cd $REMOTE_WORK_DIR &&
        
        # 导入镜像
        echo '导入 MySQL 镜像...' &&
        docker load -i mysql.tar &&
        echo '导入 Redis 镜像...' &&
        docker load -i redis.tar &&
        
        # 停止并删除旧容器（如果存在）
        docker rm -f $MYSQL_CONTAINER_NAME $REDIS_CONTAINER_NAME 2>/dev/null || true &&
        
        # 创建数据卷（如果不存在）
        docker volume create $MYSQL_DATA_VOLUME 2>/dev/null || true &&
        docker volume create $REDIS_DATA_VOLUME 2>/dev/null || true &&
        
        # 启动 MySQL 容器
        echo '启动 MySQL 容器...' &&
        docker run --name $MYSQL_CONTAINER_NAME -d \\
            --network $DOCKER_NETWORK --network-alias $MYSQL_CONTAINER_NAME \\
            -v $MYSQL_DATA_VOLUME:/var/lib/mysql \\
            -e MYSQL_RANDOM_ROOT_PASSWORD=yes \\
            -e MYSQL_DATABASE=$MYSQL_DATABASE \\
            -e MYSQL_USER=$MYSQL_USER \\
            -e MYSQL_PASSWORD=$MYSQL_PASSWORD \\
            $MYSQL_IMAGE &&
        
        # 启动 Redis 容器
        echo '启动 Redis 容器...' &&
        docker run --name $REDIS_CONTAINER_NAME -d \\
            --network $DOCKER_NETWORK --network-alias $REDIS_CONTAINER_NAME \\
            -v $REDIS_CONFIG_PATH:/usr/local/etc/redis/redis.conf \\
            -v $REDIS_DATA_VOLUME:/data \\
            $REDIS_IMAGE \\
            redis-server /usr/local/etc/redis/redis.conf \\
            --save 60 1 --loglevel warning &&
        
        # 清理镜像文件
        echo '清理镜像文件...' &&
        rm -f mysql.tar redis.tar &&
        
        echo '数据库和缓存服务初始化完成！'
    "
    
    ssh "$REMOTE_USER@$REMOTE_HOST" "$remote_init_cmd"
    
    if [[ $? -eq 0 ]]; then
        print_info "数据库和缓存服务初始化成功"
        
        # 等待服务启动
        print_info "等待服务启动..."
        sleep 10
        
        # 检查服务状态
        print_info "检查服务状态..."
        ssh "$REMOTE_USER@$REMOTE_HOST" "
            echo 'MySQL 容器状态:' &&
            docker ps | grep $MYSQL_CONTAINER_NAME &&
            echo 'Redis 容器状态:' &&
            docker ps | grep $REDIS_CONTAINER_NAME
        "
        
        return 0
    else
        print_error "数据库和缓存服务初始化失败"
        return 1
    fi
}

# 完整初始化部署（数据库 + 缓存 + 应用）
init_deploy() {
    print_info "开始完整初始化部署..."
    
    if init_services; then
        print_info "数据库和缓存服务初始化成功，开始部署应用..."
        
        if deploy_frontend && deploy_backend; then
            print_info "🎉 完整初始化部署成功！"
            print_info "MySQL 服务: $MYSQL_CONTAINER_NAME"
            print_info "Redis 服务: $REDIS_CONTAINER_NAME"
            print_info "前端访问地址: http://$REMOTE_HOST"
            print_info "后端访问地址: http://$REMOTE_HOST:$BACKEND_HOST_PORT"
        else
            print_error "应用部署失败"
            return 1
        fi
    else
        print_error "数据库和缓存服务初始化失败"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  init        初始化部署（数据库 + 缓存 + 应用）"
    echo "  frontend    仅部署前端"
    echo "  backend     仅部署后端"
    echo "  all         部署前端和后端（默认）"
    echo "  services    仅初始化数据库和缓存服务"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 init         # 首次部署（推荐）"
    echo "  $0              # 更新应用（完整部署）"
    echo "  $0 all          # 更新应用（完整部署）"
    echo "  $0 frontend     # 仅部署前端"
    echo "  $0 backend      # 仅部署后端"
    echo "  $0 services     # 仅初始化数据库和缓存"
}

# 主函数
main() {
    print_info "=== Docker 部署脚本 ==="
    print_info "项目名称: $PROJECT_NAME"
    print_info "远程服务器: $REMOTE_USER@$REMOTE_HOST"
    
    # 检查依赖
    check_dependencies
    
    # 根据参数执行相应操作
    case "${1:-all}" in
        "init")
            init_deploy
            ;;
        "services")
            init_services
            ;;
        "frontend")
            deploy_frontend
            ;;
        "backend")
            deploy_backend
            ;;
        "all")
            deploy_all
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"