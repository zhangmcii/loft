#!/bin/bash

# =============================================================================
# Docker 部署脚本模板
# 使用前请根据实际情况修改以下配置变量
# =============================================================================

# 远程服务器配置
REMOTE_USER="root"                          # 远程服务器用户名
REMOTE_HOST="your.server.com"               # 远程服务器地址

# 项目路径配置
PROJECT_ROOT="$(pwd)"                       # 项目根目录（当前目录）
FRONTEND_DIR="$PROJECT_ROOT/frontend"       # 前端项目目录
BACKEND_DIR="$PROJECT_ROOT/backend"         # 后端项目目录

# 前端部署配置
FRONTEND_BUILD_DIR="dist"                   # 前端构建输出目录
NGINX_HTML_DIR="/usr/local/nginx/html"      # Nginx静态文件目录

# 后端部署配置
DOCKER_IMAGE_NAME="your-app/backend"        # Docker镜像名称
DOCKER_CONTAINER_NAME="your-backend"        # Docker容器名称
DOCKER_PORT="5000"                          # 容器内部端口
HOST_PORT="4289"                            # 主机映射端口
DOCKER_NETWORK="database_n"                 # Docker网络名称
REMOTE_DOCKER_DIR="/root/deploy"            # 远程服务器Docker文件目录
LOG_MOUNT_PATH="/var/log/app"               # 日志挂载路径

# 数据库配置
DATABASE_URL="mysql+pymysql://user:password@mysql/dbname"  # 数据库连接URL
REDIS_URL="redis://:password@redis:6379/0"                 # Redis连接URL
REDIS_HOST="redis"                                         # Redis主机名

# 邮件配置（如需要）
MAIL_USERNAME="your-email@example.com"      # 邮箱用户名
MAIL_PASSWORD="your-mail-password"          # 邮箱密码

# 第三方服务配置（如需要）
QINIU_ACCESS_KEY="your-qiniu-access-key"    # 七牛云访问密钥
QINIU_SECRET_KEY="your-qiniu-secret-key"    # 七牛云私钥
QINIU_BUCKET_NAME="your-bucket"             # 七牛云存储桶名称
QINIU_DOMAIN="http://your-domain.com"       # 七牛云域名

# =============================================================================
# 以下为脚本逻辑，一般无需修改
# =============================================================================

# 检测操作系统和架构
detect_platform() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "Windows"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if sysctl -n machdep.cpu.brand_string | grep -q "Apple"; then
            echo "macOS-ARM"
        else
            echo "macOS-Intel"
        fi
    else
        echo "Linux"
    fi
}

# 前端构建和部署
deploy_frontend() {
    echo "开始部署前端..."
    
    # 切换到前端目录并构建
    cd "$FRONTEND_DIR" || { echo "前端目录不存在: $FRONTEND_DIR"; exit 1; }
    echo "正在构建前端项目..."
    npm run build --mode=production
    
    if [[ ! -d "$FRONTEND_BUILD_DIR" ]]; then
        echo "构建失败，$FRONTEND_BUILD_DIR 目录不存在"
        exit 1
    fi
    
    # 压缩构建文件
    echo "压缩构建文件..."
    tar -czf dist.tar.gz -C "$FRONTEND_BUILD_DIR" .
    
    # 清理远程目录
    echo "清理远程Nginx目录..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "rm -rf $NGINX_HTML_DIR/*"
    
    # 传输文件
    echo "传输文件到远程服务器..."
    scp dist.tar.gz "$REMOTE_USER@$REMOTE_HOST:$NGINX_HTML_DIR/"
    if [[ $? -eq 0 ]]; then
        echo "文件传输成功"
    else
        echo "文件传输失败"
        exit 1
    fi
    
    # 远程解压和重启Nginx
    echo "解压文件并重启Nginx..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        cd $NGINX_HTML_DIR && 
        tar -xzf dist.tar.gz --no-xattrs && 
        rm dist.tar.gz && 
        nginx -s reload
    "
    
    # 清理本地临时文件
    rm -f dist.tar.gz
    echo "前端部署完成！"
}

# 后端构建和部署
deploy_backend() {
    echo "开始部署后端..."
    
    local tar_file="${DOCKER_IMAGE_NAME##*/}_backend.tar"
    
    # 清理旧的tar文件
    if [[ -e "$tar_file" ]]; then
        rm -f "$tar_file"
        echo "已删除旧的 $tar_file"
    fi
    
    # 构建Docker镜像
    echo "构建Docker镜像..."
    cd "$PROJECT_ROOT" || exit 1
    
    local platform=$(detect_platform)
    if [[ "$platform" == "macOS-ARM" ]]; then
        echo "检测到Apple芯片，使用linux/amd64平台构建"
        docker build --platform linux/amd64 -t "$DOCKER_IMAGE_NAME" "$BACKEND_DIR"
    else
        docker build -t "$DOCKER_IMAGE_NAME" "$BACKEND_DIR"
    fi
    
    # 保存镜像为tar文件
    echo "保存Docker镜像..."
    docker save -o "$tar_file" "$DOCKER_IMAGE_NAME"
    
    # 传输到远程服务器
    echo "传输Docker镜像到远程服务器..."
    scp "$tar_file" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DOCKER_DIR/"
    if [[ $? -eq 0 ]]; then
        echo "镜像传输成功"
    else
        echo "镜像传输失败"
        exit 1
    fi
    
    # 清理本地tar文件
    rm -f "$tar_file"
    echo "已删除本地 $tar_file"
    
    # 构建远程Docker运行命令
    local remote_cmd="
        cd $REMOTE_DOCKER_DIR &&
        docker rm -f $DOCKER_CONTAINER_NAME 2>/dev/null || true &&
        docker rmi $DOCKER_IMAGE_NAME 2>/dev/null || true &&
        docker load -i $tar_file &&
        docker run --name $DOCKER_CONTAINER_NAME \
            -v $LOG_MOUNT_PATH:/home/app/logs \
            -d -p $HOST_PORT:$DOCKER_PORT \
            --network $DOCKER_NETWORK \
            -e FLASK_CONFIG=docker \
            -e DATABASE_URL='$DATABASE_URL' \
            -e MAIL_USERNAME='$MAIL_USERNAME' \
            -e MAIL_PASSWORD='$MAIL_PASSWORD' \
            -e REDIS_URL='$REDIS_URL' \
            -e REDIS_HOST='$REDIS_HOST' \
            -e QINIU_ACCESS_KEY='$QINIU_ACCESS_KEY' \
            -e QINIU_SECRET_KEY='$QINIU_SECRET_KEY' \
            -e QINIU_BUCKET_NAME='$QINIU_BUCKET_NAME' \
            -e QINIU_DOMAIN='$QINIU_DOMAIN' \
            $DOCKER_IMAGE_NAME:latest &&
        rm $tar_file
    "
    
    # 执行远程命令
    echo "在远程服务器启动容器..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "$remote_cmd"
    if [[ $? -eq 0 ]]; then
        echo "后端部署成功"
    else
        echo "后端部署失败"
        exit 1
    fi
    
    echo "后端部署完成！"
}

# 完整部署（前端+后端）
deploy_all() {
    echo "开始完整部署..."
    deploy_frontend
    deploy_backend
    echo "完整部署完成！"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  frontend    仅部署前端"
    echo "  backend     仅部署后端"
    echo "  all         部署前端和后端（默认）"
    echo "  help        显示此帮助信息"
    echo ""
    echo "使用前请确保已正确配置脚本开头的变量"
}

# 主函数
main() {
    case "${1:-all}" in
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
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"


# 使用方式：
# chmod +x deploy_template.sh
# bash deploy_template.sh frontend  # 仅部署前端
# bash deploy_template.sh backend   # 仅部署后端  
# bash deploy_template.sh all       # 部署全部