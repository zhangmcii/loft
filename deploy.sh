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
DOCKER_REGISTRY_USER="nizhenshi"  # Docker Hub 用户名或私有仓库地址
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
# 环境变量配置（后端应用）
#------------------------------------------------------------------------------
# Flask 应用配置
FLASK_CONFIG="docker"                 # Flask 配置环境

# 数据库配置
DATABASE_URL="mysql+pymysql://flasky:1234@mysql/flasky"  # 数据库连接URL

# Redis 配置
REDIS_URL="redis://:1234@myredis:6379/0"  # Redis 连接URL
REDIS_HOST="myredis"                      # Redis 主机名

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

deploy_mysql(){
  

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
    echo "示例:"
    echo "  $0              # 完整部署"
    echo "  $0 all          # 完整部署"
    echo "  $0 frontend     # 仅部署前端"
    echo "  $0 backend      # 仅部署后端"
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