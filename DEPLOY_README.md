# Docker 部署脚本使用指南

这是一个通用的 Docker 部署脚本，支持前端和后端的自动化部署。

## 🚀 快速开始

### 部署流程说明

**首次部署**：使用 `./deploy.sh init` 命令
- 自动拉取并部署 MySQL 和 Redis 服务
- 创建必要的 Docker 网络和数据卷
- 部署前端和后端应用
- 完整的环境初始化

**后续更新**：使用 `./deploy.sh` 或 `./deploy.sh all` 命令
- 仅更新应用代码（前端和后端）
- 数据库和缓存服务保持不变
- 快速更新部署

### 1. 配置部署参数

编辑 `deploy.sh` 文件顶部的配置区域：

```bash
# 修改项目基础信息
PROJECT_NAME="your_project_name"
DOCKER_REGISTRY_USER="your_dockerhub_username"

# 修改远程服务器信息
REMOTE_USER="your_username"
REMOTE_HOST="your.server.ip"

# 修改端口配置
BACKEND_HOST_PORT="4289"  # 后端服务端口

# 修改环境变量
DATABASE_URL="mysql+pymysql://user:password@host/database"
MAIL_USERNAME="your_email@example.com"
MAIL_PASSWORD="your_password"
# ... 其他配置
```

### 2. 执行部署

```bash
# 给脚本执行权限
chmod +x deploy.sh

# 首次部署（推荐）- 初始化数据库、缓存和应用
./deploy.sh init

# 后续更新部署
./deploy.sh            # 完整部署（前端 + 后端）
./deploy.sh all        # 完整部署（前端 + 后端）

# 单独部署
./deploy.sh frontend   # 仅部署前端
./deploy.sh backend    # 仅部署后端
./deploy.sh services   # 仅初始化数据库和缓存服务
```

## 📋 配置说明

### 基础项目配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `PROJECT_NAME` | 项目名称，用于命名镜像和容器 | `"flasky"` |
| `DOCKER_REGISTRY_USER` | Docker Hub 用户名或私有仓库地址 | `"nizhenshi"` |
| `BACKEND_IMAGE_NAME` | 后端镜像名称（自动生成） | `"nizhenshi/flasky_backend"` |
| `FRONTEND_IMAGE_NAME` | 前端镜像名称（自动生成） | `"nizhenshi/flasky_frontend"` |

### 远程服务器配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `REMOTE_USER` | 远程服务器用户名 | `"root"` |
| `REMOTE_HOST` | 远程服务器IP或域名 | `"192.168.1.100"` |
| `REMOTE_WORK_DIR` | 远程服务器工作目录 | `"/root/user"` |

### 前端部署配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `FRONTEND_BUILD_MODE` | 构建模式 | `"production"` |
| `FRONTEND_BUILD_DIR` | 本地构建输出目录 | `"dist"` |
| `FRONTEND_NGINX_DIR` | 远程Nginx静态文件目录 | `"/usr/local/nginx/html"` |

### 数据库和缓存服务配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `MYSQL_IMAGE` | MySQL 镜像名称 | `"mysql/mysql-server:latest"` |
| `MYSQL_CONTAINER_NAME` | MySQL 容器名称 | `"mysql"` |
| `MYSQL_DATABASE` | 数据库名称 | `"flasky"` |
| `MYSQL_USER` | 数据库用户名 | `"flasky"` |
| `MYSQL_PASSWORD` | 数据库密码 | `"1234"` |
| `REDIS_IMAGE` | Redis 镜像名称 | `"redis:latest"` |
| `REDIS_CONTAINER_NAME` | Redis 容器名称 | `"myredis"` |
| `REDIS_PASSWORD` | Redis 密码 | `"1234"` |
| `REDIS_CONFIG_PATH` | Redis 配置文件路径 | `"/root/user/blog/redis.conf"` |

### 后端部署配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `BACKEND_HOST_PORT` | 宿主机端口 | `"4289"` |
| `BACKEND_CONTAINER_PORT` | 容器内端口 | `"5000"` |
| `LOG_MOUNT_PATH` | 宿主机日志目录 | `"/var/log/loft"` |
| `CONTAINER_LOG_PATH` | 容器内日志目录 | `"/home/flasky/logs"` |
| `DOCKER_NETWORK` | Docker 网络名称 | `"database_n"` |

### 环境变量配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `FLASK_CONFIG` | Flask 配置环境 | `"docker"` |
| `DATABASE_URL` | 数据库连接URL | `"mysql+pymysql://user:pass@host/db"` |
| `REDIS_URL` | Redis 连接URL | `"redis://:pass@host:6379/0"` |
| `MAIL_USERNAME` | 邮件服务用户名 | `"your_email@example.com"` |
| `MAIL_PASSWORD` | 邮件服务密码 | `"your_password"` |
| `QINIU_ACCESS_KEY` | 七牛云 Access Key | `"your_access_key"` |
| `QINIU_SECRET_KEY` | 七牛云 Secret Key | `"your_secret_key"` |
| `QINIU_BUCKET_NAME` | 七牛云存储桶名称 | `"your_bucket"` |
| `QINIU_DOMAIN` | 七牛云域名 | `"http://your.domain.com"` |

## 🔧 前置要求

### 本地环境
- Docker
- SSH 客户端
- SCP 工具
- Node.js 和 npm（用于前端构建）

### 远程服务器
- Docker
- Nginx（用于前端静态文件服务）
- 相应的数据库服务（MySQL/Redis 等）

## 📁 项目结构要求

```
your_project/
├── deploy.sh           # 部署脚本
├── frontend/           # 前端项目目录
│   ├── package.json
│   ├── src/
│   └── ...
├── backend/            # 后端项目目录
│   ├── Dockerfile
│   ├── app/
│   └── ...
└── DEPLOY_README.md    # 本说明文档
```

## 🚨 注意事项

1. **SSH 密钥配置**：确保本地机器可以通过 SSH 密钥免密登录远程服务器
2. **Docker 网络**：确保远程服务器上存在指定的 Docker 网络
3. **端口冲突**：检查指定端口是否被占用
4. **权限问题**：确保远程用户有 Docker 操作权限
5. **防火墙设置**：确保相关端口在防火墙中开放

## 🔍 故障排除

### 常见问题

1. **SSH 连接失败**
   ```bash
   # 测试 SSH 连接
   ssh your_user@your_host
   ```

2. **Docker 构建失败**
   ```bash
   # 本地测试构建
   docker build -t test_image ./backend
   ```

3. **端口被占用**
   ```bash
   # 检查端口占用
   ssh your_user@your_host "netstat -tlnp | grep :4289"
   ```

4. **Nginx 配置问题**
   ```bash
   # 检查 Nginx 状态
   ssh your_user@your_host "nginx -t && systemctl status nginx"
   ```

5. **数据库连接失败**
   ```bash
   # 检查 MySQL 容器状态
   ssh your_user@your_host "docker logs mysql"
   
   # 检查数据库连接
   ssh your_user@your_host "docker exec -it mysql mysql -u flasky -p"
   ```

6. **Redis 连接失败**
   ```bash
   # 检查 Redis 容器状态
   ssh your_user@your_host "docker logs myredis"
   
   # 测试 Redis 连接
   ssh your_user@your_host "docker exec -it myredis redis-cli -a 1234"
   ```

7. **初始化失败**
   ```bash
   # 清理环境重新初始化
   ssh your_user@your_host "docker rm -f mysql myredis && docker volume rm mysql_data redis_data"
   ./deploy.sh init
   ```

### 日志查看

```bash
# 查看容器日志
ssh your_user@your_host "docker logs your_container_name"

# 查看 Nginx 日志
ssh your_user@your_host "tail -f /var/log/nginx/error.log"
```

## 🎯 自定义扩展

如需添加更多功能，可以在脚本中添加新的函数：

```bash
# 添加数据库备份功能
backup_database() {
    print_info "开始数据库备份..."
    # 备份逻辑
}

# 添加健康检查功能
health_check() {
    print_info "执行健康检查..."
    # 健康检查逻辑
}
```

## 📞 支持

如有问题，请检查：
1. 配置是否正确
2. 网络连接是否正常
3. 服务器资源是否充足
4. 相关服务是否正常运行