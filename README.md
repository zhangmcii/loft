# 🌟 The-Reverie-Loft(随想阁楼) - 移动端社交平台

> 一个基于 Vue3 + Flask 的移动端优先的社交平台

[![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![Vue.js](https://img.shields.io/badge/Vue-3.x-brightgreen)](https://vuejs.org/)[![Flask](https://img.shields.io/badge/Flask-3.x-blue)](https://flask.palletsprojects.com/)

## 📖 项目简介

The-Reverie-Loft(随想阁楼) 是一个专为移动端设计的社交平台，提供完整的社交功能体验。项目采用前后端分离架构，前端使用 Vue3 构建移动端界面，后端基于 Flask 提供稳定的 API 服务。

### 移动端界面
![登录页面](./docs/登录页面.png)
![用户首页](./docs/用户首页.png)
![个人资料1](./docs/个人资料1.png)
![个人资料2](./docs/个人资料2.png)
![聊天](./docs/聊天.png)
![文章详情](./docs/文章详情.png)
![评论详情](./docs/评论详情.png)
![通知面板](./docs/通知面板.png)
![发布文章](./docs/发布文章.png)
![管理员日志页](./docs/管理员日志页.png)
![绑定邮箱页面](./docs/绑定邮箱页面.png)

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

  
- 🔐 **安全与管理**
  - JWT 权限验证
  - 用户角色管理（普通用户、内容管理员、管理员）
  - 评论敏感词过滤
  - 图文请求次数限制
  - 邮件告警


## 🛠 技术栈

### 前端技术

- **框架**: Vue 3.x
- **构建工具**: Vite
- **UI 组件**: Element Plus / Vant / undraw UI
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
│   │   ├── main/            # 主要业务接口(现已使用api/)  
│   │   ├── mycelery/        # Celery 任务  
│   │   ├── schemas/         # 表单验证  
│   │   ├── templates/       # 模板文件  
│   │   └── utils/           # 工具函数  
│   │   └── models.py        # 数据模型  
│   ├── migrations/          # 数据库迁移文件  
│   ├── requirements/        # Python 依赖  
│   ├── tests_api/           # API 测试  
│   └── deploy/              # 部署配置  
│  
└── docs/                    # README.md中的预览图片
└── deploy.sh                # docker部署
└── start.sh                 # 前后端启动脚本
└── .pre-commit-config.yaml  # 代码规范工具
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
# 平台本地运行端口号
VITE_PORT=5172
VITE_BASE=/

# 图片域名
VITE_QINIU_DOMAIN=QINIU_DOMAIN
# 七牛云bucket名称
VITE_QINIU_BUCKET=QINIU_BUCKET

# 后端代理地址
VITE_APP_BASE_API = '/api'

# ICP 备案号
VITE_ICP=xxxx
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
celery -A app.make_celery worker --loglevel INFO -P eventlet # windows
celery -A app.make_celery worker --loglevel INFO    # mac

# 8. 启动后端服务  
python flasky.py  
```

后端服务将在 `http://localhost:8082` 启动

### 🎨 前端启动

```bash
# 1. 进入前端目录  
cd frontend  

# 2. 安装依赖  
npm install  

# 3. 启动开发服务器  
npm run dev  

```

前端服务将在 `http://localhost:5172` 启动

### 如何成为超级管理员身份？
配置backend/config.py中的FLASKY_ADMIN变量
当你绑定的邮箱与后端配置的邮箱相同时，该账号将具有管理员的权限。
拥有管理员的权限， 你将可以对所有的评论审核，增加/删除tag标签，帮助未绑定邮箱的用户找回密码！
![管理员邮箱配置](./docs/管理员邮箱配置.png)
![管理员页面](./docs/管理员页面.png)

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
2. 提供详细的描述和复现步骤

### 开发环境设置

```bash
# 安装开发依赖  
cd frontend && npm install  
cd backend && pip install -r requirements/dev.txt  

# 后端测试
cd backend/tests_api
pytest -v        # 

# 代码格式化  
pre-commit install
pre-commit run --all-files
```

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源协议。


## 🙏 致谢

在本项目的开发过程中，参考了以下开源项目和资料，特此致谢：

- **用户资料设计灵感**  
  - [leleo-home-page](https://github.com/leleo886/leleo-home-page) 

- **网站引导页部分实现借鉴**  
  - [Blog-Index](https://github.com/EsunR/Blog-Index)

- **设计思路**  
  - Miguel Grinberg 著，《Flask Web开发：基于 Python 的 Web 应用开发实战（第二版）》

## 📞 联系我们

- 问题反馈: https://github.com/nizhensh-i/The-Reverie-Loft/issues
- 邮箱: zmc_li@foxmail.com

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！