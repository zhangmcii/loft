# 社交平台项目

> 一个基于 Vue + Flask 的前后端分离社交平台

## 🚀 快速开始

### 前端启动

```bash
# 1. 克隆项目
git clone xx

# 2. 安装依赖
npm install

# 3. 配置环境变量
# 复制 .env.example 到 .env 并修改相关配置
cp .env.example .env

# 4. 启动开发服务器
npm run dev
```

### 后端启动

```bash
# 1. 创建虚拟环境

# 2. 进入后端目录
cd blog_backend

# 3. 安装依赖
pip install -r ./requirements/dev.txt

# 4. 初始化角色（仅首次启动需要）
flask shell
# 在 shell 中执行:
Role.insert_roles()
# 然后退出 shell:
exit()

# 5. 配置环境变量
# 复制 .env.example 到 .env 并修改相关配置
cp .env.example .env

# 6. 启动后端服务（确保 Redis 已启动）
python flasky.py
```

## 📋 功能介绍

- **用户系统**

  - 注册、登录
  - 上传用户头像和兴趣封面
  - 修改密码（支持邮箱验证码）
  - 绑定邮箱（支持邮箱验证码）

- **内容发布**

  - 发布文章（支持富文本和图片上传）
  - 评论文章
  - 点赞文章
  - 回复评论
  - 点赞评论

- **社交功能**

  - 用户关注
  - 私信聊天
  - 消息推送（@提及、评论、点赞、私信）

- **安全与管理**
  - JWT 权限验证
  - 用户角色管理（普通用户、内容管理员、管理员）
  - 评论敏感词过滤
  - 图文请求次数限制

## 🔧 项目依赖

### 前置条件

1. **七牛云账号**

   - 需要 accesskey、secretkey、bucket 和域名
   - 用于存储用户图像、文章图片和资料卡兴趣图片
   - [如何获取七牛云凭证](https://download.csdn.net/blog/column/11693119/132181583)

2. **QQ 邮箱授权码**

   - 用于账号邮件绑定和密码找回
   - [如何获取 QQ 邮箱授权码](https://blog.csdn.net/weixin_68846313/article/details/147430548)

3. **数据库**
   - MySQL：存储结构化数据
   - Redis：用于 Celery 异步任务、WebSocket 用户状态、邮件验证码和请求限制

## 🏗️ 技术架构

### 前端技术栈

- Vue 3
- Vue Router
- Pinia
- Axios
- Scss
- Socket.io
- Qiniu-js

### 后端技术栈

- Flask
- Flask-JWT-Extended
- Flask-SQLAlchemy
- Flask-Limiter
- Flask-SocketIO
- Celery
- Redis
- MySQL

## 🌐 生产环境部署

支持 Docker 部署：

```bash
# 1. 修改后端项目中的 deploy.sh 文件
# 2. 更改第一行为前端项目在本机的绝对位置
# 例如：source /path/to/your/blog_front/front.sh

# 3. 修改环境变量和远程主机信息
# 修改 remote_cmd_backend 命令中的环境变量值
# 修改 ROMOTE_USER 和 ROMOTE_HOST 为远程主机的用户名和主机名

# 4. 进入后端目录
cd blog_backend

# 5. 执行部署脚本
./deploy.sh
```

部署后可通过 `http://服务器IP:1717` 访问（需确保服务器已开放该端口）

## 📦 技术组件说明

| 组件    | 用途                                                          |
| ------- | ------------------------------------------------------------- |
| MySQL   | 存储结构化数据                                                |
| Redis   | Celery 异步任务代理、WebSocket 用户状态、邮件验证码、请求限制 |
| 七牛云  | 存储用户图像、文章图片、资料卡兴趣图片                        |
| QQ 邮箱 | 账号邮件绑定、找回密码邮件验证                                |
| Nginx   | 部署前端                                                      |
| Docker  | 部署 Flask 应用、MySQL、Redis（生产环境）                     |

## 📸 项目界面预览

> 以下是项目主要功能界面的截图展示

<!--
在此处添加项目截图，建议按以下格式：

### 首页/动态流
![首页界面](path/to/home_screenshot.png)

### 文章详情
![文章详情](path/to/post_detail_screenshot.png)

### 用户个人主页
![用户主页](path/to/profile_screenshot.png)

### 消息中心
![消息中心](path/to/message_screenshot.png)
-->

## 🔗 在线体验

访问：[www.xx.com](http://www.xx.com)

---

_本项目基于《Flask Web 开发》(狗书)项目扩展而成，将原服务端渲染模式改为前后端分离模式。_
