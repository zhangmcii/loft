# 🌟 The Reverie Loft(随想阁楼) - 移动端社交平台

> 一个基于 Vue3 + Flask 的现代化移动端社交应用

[![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![Vue.js](https://img.shields.io/badge/Vue-3.x-brightgreen)](https://vuejs.org/)[![Flask](https://img.shields.io/badge/Flask-3.x-blue)](https://flask.palletsprojects.com/)

## 📖 项目简介

The Reverie Loft 是一个专为移动端设计的社交平台，提供完整的社交功能体验。项目采用前后端分离架构，前端使用 Vue3 构建响应式移动端界面，后端基于 Flask 提供稳定的 API 服务。

## 🎨 项目预览

### 移动端界面

### 功能演示

### 界面截图

## ✨ 功能特性

- 🔐 **用户系统**
  
  - 用户注册与登录
  - 个人资料管理
  - 头像上传
  - 密码找回（支持邮箱验证码）
- 📝 **内容发布**
  
  - 图文动态发布
  - 多图片上传
  - 富文本编辑
- 💬 **社交互动**
  
  - 点赞
  - 评论与回复
  - 关注与粉丝
  - 私信聊天
- 🔔 **实时通知**
  
  - 消息推送（@提及、评论、点赞、私信）
  - 互动提醒

  
- 🛠️ **安全与管理**
  - JWT 权限验证
  - 用户角色管理（普通用户、内容管理员、管理员）
  - 评论敏感词过滤
  - 图文请求次数限制
  - 邮件告警


## 🛠 技术栈

### 前端技术

- **框架**: Vue 3.x
- **构建工具**: Vite
- **UI 组件**: Element Plus / Vant
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **样式**: SCSS

### 后端技术

- **框架**: Flask 3.x
- **数据库**: MySQL
- **ORM**: SQLAlchemy
- **认证**: JWT
- **任务队列**: Celery + Redis
- **文件存储**: 本地存储 / 云存储

### 开发工具

- **代码规范**:ESLint + Prettier + flake8 + black + isort
- **版本控制**: Git
- **包管理**: npm
- **容器化**: Docker

## 📁 目录结构

```
loft_1/  
├── frontend/                 # 前端项目目录  
│   ├── src/  
│   │   ├── api/             # API 接口封装  
│   │   ├── asset/           # 静态资源  
│   │   ├── config/          # 配置文件  
│   │   ├── directives/      # Vue 指令  
│   │   ├── plugins/         # 插件配置  
│   │   ├── router/          # 路由配置  
│   │   ├── stores/          # Pinia 状态管理  
│   │   ├── utils/           # 工具函数  
│   │   └── views/           # 页面组件  
│   ├── public/              # 公共静态文件  
│   ├── dist/                # 构建输出目录  
│   ├── package.json         # 前端依赖配置  
│   └── vite.config.js       # Vite 配置  
│  
├── backend/                  # 后端项目目录  
│   ├── app/  
│   │   ├── api/             # API 路由  
│   │   ├── auth/            # 认证模块  
│   │   ├── main/            # 主要业务逻辑  
│   │   ├── mycelery/        # Celery 任务  
│   │   ├── schemas/         # 数据模型  
│   │   ├── templates/       # 模板文件  
│   │   └── utils/           # 工具函数  
│   ├── migrations/          # 数据库迁移文件  
│   ├── requirements/        # Python 依赖  
│   ├── tests_api/           # API 测试  
│   ├── tests_main/          # 主要功能测试  
│   └── deploy/              # 部署配置  
│  
└── README.md                # 项目说明文档  
```

## 🚀 环境准备

### 📋 系统要求

- **Node.js** >= 16.0.0
- **Python** >= 3.8
- **MySQL** >= 8.0
- **Redis** >= 6.0

### ⚙️ 配置文件

#### 1. 后端环境配置

在 `backend/` 目录下创建 `.env` 文件：

```bash
# 数据库配置  
DATABASE_URL=mysql://username:password@localhost:3306/loft_db  

# Redis 配置  
REDIS_URL=redis://localhost:6379/0  

# JWT 密钥  
JWT_SECRET_KEY=your-super-secret-jwt-key  

# 邮件配置 (QQ邮箱示例)  
MAIL_SERVER=smtp.qq.com  
MAIL_PORT=587  
MAIL_USE_TLS=True  
MAIL_USERNAME=your-email@qq.com  
MAIL_PASSWORD=your-qq-auth-code  # QQ邮箱授权码，不是登录密码  

# 七牛云配置 (如果使用)  
QINIU_ACCESS_KEY=your-qiniu-access-key  
QINIU_SECRET_KEY=your-qiniu-secret-key  
QINIU_BUCKET_NAME=your-bucket-name  
QINIU_DOMAIN=your-qiniu-domain  

# 应用配置  
FLASK_ENV=development  
SECRET_KEY=your-flask-secret-key  
```

#### 2. 前端环境配置

在 `frontend/` 目录下创建 `.env` 文件：

```bash
# API 基础地址  
VITE_API_BASE_URL=http://localhost:5000  

# 应用配置  
VITE_APP_TITLE=Loft 社交平台  
```

### 🗄️ 数据库初始化

```bash
# 创建数据库 (MySQL 示例)  
mysql -u root -p  
CREATE DATABASE loft_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;  

# 或者 PostgreSQLpsql -U postgres  
CREATE DATABASE loft_db;  
```

## 🏃‍♂️ 启动方式

### 🔧 后端启动

```bash
# 1. 进入后端目录  
cd backend  

# 2. 创建虚拟环境  
python -m venv venv  

# 3. 激活虚拟环境  
# Windows  
venv\Scripts\activate  
# macOS/Linux  
source venv/bin/activate  

# 4. 安装依赖  
pip install -r requirements/base.txt  

# 5. 数据库迁移  
flask db upgrade  

# 6. 启动 Redis (另开终端)  
redis-server  

# 7. 启动 Celery 异步任务 (另开终端)  
celery -A app.mycelery.celery worker --loglevel=info  

# 8. 启动后端服务  
python run.py  
```

后端服务将在 `http://localhost:8082` 启动

### 🎨 前端启动

```bash
# 1. 进入前端目录  
cd frontend  

# 2. 安装依赖  
npm install  
# 或者使用 yarnyarn install  

# 3. 启动开发服务器  
npm run dev  
# 或者  
yarn dev  
```

前端服务将在 `http://localhost:5172` 启动

## 🐳 部署说明

### Docker 部署 (推荐)

```bash

```

### 手动部署

#### 后端部署

```bash
# 生产环境依赖  
pip install -r requirements/prod.txt  

# 配置生产环境变量  
export FLASK_ENV=production  
export DATABASE_URL=your_production_db_url  

# 数据库迁移  
flask db upgrade  

# 使用 Gunicorn 启动  
gunicorn -w 4 -b 0.0.0.0:5000 app:app  
```

#### 前端部署

```bash
# 构建生产版本  
npm run build  

# 部署到 Nginx 或其他 Web 服务器  
# 将 dist/ 目录内容复制到服务器  
```

### Nginx 配置示例

```nginx
server {  
    listen 80;    
    server_name your-domain.com;  

    # 前端静态文件  
    location / {        
        root   /usr/local/nginx/html;
        index  index.html;
        try_files $uri $uri/ /index.html;
    }  

    # 反向代理到Flask应用的后端接口
    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://localhost:4289;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /;
    }
    
    # 反向代理到Flask应用的websocket接口
    location /socket.io/ {
        proxy_pass http://localhost:4289;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

}  
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请遵循以下步骤：

### 提交代码

1. **Fork 项目** 到你的 GitHub 账户
2. **创建功能分支**: `git checkout -b feature/amazing-feature`
3. **提交更改**: `git commit -m 'Add some amazing feature'`
4. **推送分支**: `git push origin feature/amazing-feature`
5. **创建 Pull Request**

### 提交 Issue

如果你发现了 bug 或有功能建议，请：

1. 检查是否已有相关 Issue
2. 使用合适的 Issue 模板
3. 提供详细的描述和复现步骤
4. 添加相关的标签

### 开发环境设置

```bash
# 安装开发依赖  
cd frontend && npm install  
cd backend && pip install -r requirements/dev.txt  

# 运行测试  
npm run test        # 前端测试  
pytest             # 后端测试  

# 代码格式化  
npm run lint:fix    # 前端代码格式化  
black .            # 后端代码格式化  
```

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源协议。


## 🙏 致谢

本项目部分设计思路参考了 Miguel Grinberg 的《Flask Web开发（第二版）》一书，在此致谢。

## 📞 联系我们

- 项目主页: https://github.com/your-username/loft_1
- 问题反馈: https://github.com/your-username/loft_1/issues
- 邮箱: zmc_li@foxmail.com

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！