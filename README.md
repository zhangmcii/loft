<div align="center">

# Loft

### 一个现代化、功能丰富的社交平台

**基于 Vue3 + Flask 构建的开源社交系统**

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1.svg)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-7.x-DC382D.svg)](https://redis.io/)

[功能演示](#-功能特性) • [快速上手](#-快速上手) • [配置指南](#-配置指南) • [部署文档](#-部署指南) • [FAQ](#-常见问题)

![Loft Screenshot](docs/screenshot-placeholder.png)
*现代化社交平台界面设计*

</div>

---

## 📖 项目简介

Loft 是一个全栈开源社交平台项目，采用现代化的技术栈构建，提供丰富的社交功能和优秀的用户体验。

### ✨ 核心功能

- 👤 **用户系统**：注册、登录、个人资料管理
- 📱 **第三方登录**：支持 GitHub、Google、QQ、微博 OAuth
- 💬 **实时聊天**：基于 WebSocket 的即时通讯
- 📝 **内容发布**：支持文字、图片动态发布
- 👍 **互动功能**：点赞、评论、关注
- 🔐 **权限管理**：基于 JWT 的安全认证
- 📊 **数据分析**：操作日志、用户行为统计
- 🎨 **响应式设计**：完美支持 PC 和移动端

### 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 + Vite | 现代化构建工具与响应式框架 |
| | Element Plus | 优雅美观的 UI 组件库 |
| | Vue Router | 前端路由管理 |
| | Pinia | 状态管理 |
| **后端** | Flask 3 | 轻量级 Python Web 框架 |
| | SQLAlchemy | ORM 数据库操作 |
| | Flask-JWT-Extended | JWT 认证 |
| | Flask-SocketIO | WebSocket 实时通信 |
| **数据库** | MySQL 8+ | 关系型数据存储 |
| | Redis | 缓存、会话、消息队列 |
| **部署** | Docker | 容器化部署 |
| | Nginx | 反向代理与静态文件服务 |

---

## 🚀 快速上手

### 前置要求

- [Docker](https://www.docker.com/) 20.10+
- [Docker Compose](https://docs.docker.com/compose/) 2.0+
- [Git](https://git-scm.com/)

### ⚡ 三步启动项目

#### 第一步：克隆仓库

```bash
git clone https://github.com/your-username/loft.git
cd loft
```

#### 第二步：配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 🚨 重要：使用编辑器打开 .env 文件，填写所有必填项
# 推荐使用 VSCode: code .env
# 或 Vim: vim .env
```

**关键配置项：**
- `SECRET_KEY` 和 `JWT_SECRET_KEY`：务必修改为随机字符串
- 数据库密码：替换所有的 `your-mysql-password`
- QQ 邮箱授权码：在 QQ 邮箱设置中生成
- 七牛云凭证：注册七牛云并创建存储空间
- OAuth 应用：至少配置一个第三方登录

#### 第三步：一键启动

```bash
# 启动所有服务（MySQL + Redis + Flask + Nginx）
docker-compose up -d

# 查看启动状态
docker-compose ps

# 查看实时日志
docker-compose logs -f
```

🎉 **恭喜！** 项目启动成功后，访问 `https://localhost` 即可体验。

---

## 🔧 配置指南

### 📋 环境变量清单

| 变量名 | 说明 | 是否必填 | 申请/配置指引 |
|--------|------|----------|---------------|
| `SECRET_KEY` | Flask 应用密钥 | ✅ | `openssl rand -hex 32` 生成 |
| `JWT_SECRET_KEY` | JWT 令牌密钥 | ✅ | `openssl rand -hex 32` 生成 |
| `FLASKY_ADMIN_MAIL` | 管理员邮箱 | ✅ | 设置为你的邮箱 |
| **MySQL 配置** | | | |
| `DATABASE_URL` | 生产数据库连接 | ✅ | 格式见下方示例 |
| `DEV_DATABASE_URL` | 开发数据库连接 | ✅ | 本地开发使用 |
| **QQ 邮箱** | | | |
| `MAIL_USERNAME` | QQ 邮箱地址 | ✅ | 你的 QQ 邮箱 |
| `MAIL_PASSWORD` | 邮箱授权码 | ✅ | [QQ邮箱设置](https://mail.qq.com/) → 账户 → SMTP |
| **七牛云** | | | |
| `QINIU_ACCESS_KEY` | 七牛云 AK | ✅ | [七牛云控制台](https://portal.qiniu.com/) |
| `QINIU_SECRET_KEY` | 七牛云 SK | ✅ | 密钥管理 |
| `QINIU_BUCKET_NAME` | 存储空间名 | ✅ | 创建 Bucket |
| `QINIU_DOMAIN` | 七牛云域名 | ✅ | 自定义域名或测试域名 |
| **OAuth 登录** | | | |
| `GITHUB_CLIENT_ID` | GitHub OAuth ID | ⭐ | [GitHub开发者](https://github.com/settings/developers) |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth 密钥 | ⭐ | 创建 OAuth App |
| `GOOGLE_CLIENT_ID` | Google OAuth ID | ⭐ | [Google Cloud](https://console.cloud.google.com/apis/credentials) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 密钥 | ⭐ | 需要配置 OAuth 同意屏幕 |

**⭐ 说明：** OAuth 配置为可选，但建议至少配置一个，否则用户只能账号注册。

### 🔍 配置示例

```bash
# MySQL 配置示例
# 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
DATABASE_URL=mysql+pymysql://root:your-strong-password@mysql:3306/loft_prod?charset=utf8mb4

# Redis 配置（Docker 部署）
# 使用容器名: redis
REDIS_HOST=redis

# 七牛云域名示例
QINIU_DOMAIN=https://your-bucket-name.bkt.clouddn.com
```

---

## 📦 部署指南

### 🐳 Docker 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                     Nginx (端口 80/443)                  │
│  ┌──────────────┬──────────────┬──────────────────┐    │
│  │  静态文件    │  API 代理    │  WebSocket 代理  │    │
│  │  (Vue构建)   │  (/api/*)    │  (/socket.io/*)  │    │
│  └──────────────┴──────────────┴──────────────────┘    │
└─────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼─────┐   ┌────▼─────┐   ┌─────▼──────┐
        │ Flask App │   │  MySQL   │   │   Redis    │
        │ (Python)  │   │ (数据库)  │   │  (缓存)    │
        └───────────┘   └──────────┘   └────────────┘
```

### 📁 目录映射说明

启动 Docker 容器后，以下目录会自动创建并映射：

```bash
# 在宿主机上创建的数据持久化目录
./data/
├── mysql/          # MySQL 数据文件
│   ├── data/       # 数据库文件
│   └── logs/       # 数据库日志
├── redis/          # Redis 数据
│   └── data/       # AOF 持久化文件
├── logs/           # 应用日志
│   ├── backend/    # Flask 应用日志
│   └── nginx/      # Nginx 访问和错误日志
└── ssl/            # SSL 证书（可选）
    ├── cert.pem    # 证书文件
    └── key.pem     # 私钥文件
```

### 🔒 SSL 证书配置

#### 方法一：使用 Let's Encrypt（推荐）

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书（自动配置 Nginx）
sudo certbot --nginx -d your-domain.com

# 证书自动续期
crontab -e
# 添加: 0 12 * * * certbot renew --quiet
```

#### 方法二：手动配置已有证书

```bash
# 1. 将证书文件复制到 ssl 目录
cp your-cert.pem ./data/ssl/cert.pem
cp your-key.pem ./data/ssl/key.pem

# 2. 修改 docker-compose.yml 中的 Nginx 配置
# 取消 SSL 相关配置的注释

# 3. 重启服务
docker-compose restart nginx
```


### 🌐 Nginx 配置说明

项目使用 Docker 内的 Nginx，配置文件位于 `docker/nginx/nginx.conf`。主要配置项：

```nginx
# 需要修改的配置项
server {
    listen 80;
    server_name your-domain.com;  # ⭐ 修改为你的域名
    
    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://backend:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket 代理
    location /socket.io/ {
        proxy_pass http://backend:5000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 🔄 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重建并启动服务（会保留数据库数据）
docker-compose up -d --build

# 查看更新日志
docker-compose logs -f --tail=100
```

---

## ❓ 常见问题

### 1. ❌ 容器无法连接 MySQL 数据库

**错误现象：**
```
SQLAlchemy Error: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")
```

**排查步骤：**

1. **检查 MySQL 容器状态**
   ```bash
   docker-compose ps mysql
   docker-compose logs mysql
   ```

2. **验证数据库密码**
   ```bash
   # 进入 MySQL 容器
   docker-compose exec mysql mysql -uroot -p
   # 输入你在 .env 中设置的密码
   ```

3. **检查网络连接**
   ```bash
   # 进入 Flask 容器
   docker-compose exec backend bash
   # 在容器内测试连接
   nc -zv mysql 3306
   ```

4. **确认 .env 配置**
   - 检查 `DATABASE_URL` 中的密码是否正确
   - 确认使用 `mysql` 作为主机名（Docker 网络）
   - 格式：`mysql+pymysql://root:密码@mysql:3306/数据库名`

**解决方案：**
```bash
# 如果修改了密码，需要重建数据库容器
docker-compose down mysql
docker volume rm loft_mysql_data  # 注意：这会删除数据！
docker-compose up -d mysql
```

---

### 2. ❌ 七牛云上传返回 401 Unauthorized

**错误现象：**
```json
{"error": "bad token", "code": 401}
```

**排查步骤：**

1. **检查密钥配置**
   ```bash
   # 确认 .env 中的密钥没有多余空格
   QINIU_ACCESS_KEY=your-access-key  # ✅ 正确
   QINIU_ACCESS_KEY = your-access-key  # ❌ 错误（等号两边不能有空格）
   ```

2. **验证密钥有效性**
   ```bash
   # 安装七牛云命令行工具
   npm install -g qiniu-cli
   
   # 登录测试
   qiniu account your-ak your-sk
   qiniu listbucket your-bucket-name
   ```

3. **检查存储空间和域名**
   - 确认 `QINIU_BUCKET_NAME` 与控制台一致
   - 确认 `QINIU_DOMAIN` 已配置并可访问
   - 域名必须以 `http://` 或 `https://` 开头

**解决方案：**
```bash
# 重新生成七牛云密钥
# 1. 登录七牛云控制台
# 2. 个人中心 → 密钥管理 → 创建新密钥
# 3. 更新 .env 文件
# 4. 重启服务
docker-compose restart backend
```

---

### 3. ❌ QQ 邮箱授权码失效（535 Error）

**错误现象：**
```
SMTPAuthenticationError: (535, b'Error: authentication failed')
```

**原因分析：**
QQ 邮箱授权码有效期有限，或 SMTP 服务未开启。

**解决方案：**

1. **重新生成授权码**
   ```
   登录 QQ 邮箱 → 设置 → 账户 →
   POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务 →
   生成授权码
   ```

2. **验证 SMTP 配置**
   ```python
   # 使用 Python 测试脚本
   import smtplib
   from email.mime.text import MIMEText
   
   smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
   smtp.login('your-qq@qq.com', 'your-authorization-code')
   ```

3. **更新 .env 并重启**
   ```bash
   # 修改 .env 中的 MAIL_PASSWORD
docker-compose restart backend
   ```

---

### 4. ❌ OAuth 登录跳转失败（redirect_uri_mismatch）

**错误现象：**
```
OAuth Error: redirect_uri_mismatch
```

**排查步骤：**

1. **检查回调地址配置**
   ```bash
   # 各平台的回调地址格式：
   GitHub: https://your-domain.com/api/auth/oauth/callback/github
   Google: https://your-domain.com/api/auth/oauth/callback/google
   QQ:     https://your-domain.com/api/auth/oauth/callback/qq
   微博:   https://your-domain.com/api/auth/oauth/callback/weibo
   ```

2. **确认域名配置**
   - 检查 `FRONTEND_OAUTH_REDIRECT` 是否设置为你的域名
   - 检查 OAuth 平台配置的域名是否包含协议（http/https）

**解决方案：**

```bash
# 更新 .env 中的回调域名
FRONTEND_OAUTH_REDIRECT=https://your-domain.com/oauth/callback

# 重启服务
docker-compose restart backend

# 在 OAuth 平台重新配置回调地址
# 注意：
# - 不要遗漏 /api 前缀
# - 确保使用 https（生产环境）
```

---

### 5. ❌ WebSocket 连接失败（502 Bad Gateway）

**错误现象：**
浏览器控制台：
```
WebSocket connection to 'wss://your-domain.com/socket.io/...' failed: 502
```

**排查步骤：**

1. **检查 Nginx 配置**
   ```bash
   # 确认 nginx.conf 中包含 WebSocket 代理配置
   location /socket.io/ {
       proxy_pass http://backend:5000/socket.io/;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
   }
   ```

2. **验证 SocketIO 服务**
   ```bash
   # 查看 Flask 应用日志
   docker-compose logs backend | grep socketio
   
   # 进入容器测试
   docker-compose exec backend bash
   curl http://localhost:5000/socket.io/
   ```

3. **检查防火墙/安全组**
   - 确认服务器安全组开放 80/443 端口
   - 检查是否有 CDN/Web 应用防火墙拦截 WebSocket

**解决方案：**

```bash
# 重建 nginx 容器
docker-compose down nginx
docker-compose up -d nginx

# 如果使用 Cloudflare 等 CDN，需要开启 WebSocket 支持
# Cloudflare: 网络 → WebSockets → 开启
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发环境搭建

```bash
# 后端开发
cd backend
pip install -r requirements/dev.txt
python flasky.py run

# 前端开发
cd frontend
npm install
npm run dev
```

---

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## ⭐ Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/loft&type=Date)](https://star-history.com/#your-username/loft&Date)

---

## 📞 联系方式

- 📧 项目维护者: your-email@example.com
- 🐛 Bug 反馈: [提交 Issue](https://github.com/your-username/loft/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by [Your Name](https://github.com/your-username)

</div>
