# 第三方登录系统使用说明

## 概述

本项目基于 `senweaver-oauth` 库实现了一个可扩展的第三方登录系统，支持多种 OAuth 平台的统一登录。

## 架构设计

### 核心特点

1. **统一的 OAuth 处理逻辑** - 所有平台共享同一套代码，避免重复开发
2. **配置驱动** - 通过环境变量控制平台启用状态
3. **可扩展性强** - 新增平台只需添加配置，无需修改代码逻辑
4. **用户自动创建** - 首次登录自动创建用户账号并绑定第三方账号
5. **前后端分离** - 使用弹窗 + postMessage 机制，适合 SPA 应用

## 后端实现

### 文件结构

```
backend/app/auth/
├── __init__.py               # 蓝图初始化
├── views.py                  # 路由定义
└── third_party_login.py      # OAuth 核心逻辑
```

### 核心接口

#### 1. 获取可用的 OAuth 提供商

```
GET /auth/oauth/providers
```

响应示例：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "provider": "github",
      "name": "GitHub",
      "enabled": true
    }
  ]
}
```

#### 2. OAuth 登录发起

```
GET /auth/oauth/<provider>/login
```

参数：
- `provider`: 平台标识（github, gitee, qq, wechat 等）

返回：重定向到第三方授权页面

#### 3. OAuth 回调处理

```
GET /auth/oauth/<provider>/callback
```

参数：
- `code`: 授权码
- `state`: 状态参数

返回：HTML 页面，通过 postMessage 通信

### 数据库模型

#### User 表（已有）

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    nickname = db.Column(db.String(64))
    image = db.Column(db.String(255))  # 头像
    # ... 其他字段
```

#### ThirdPartyAccount 表（新增）

```python
class ThirdPartyAccount(db.Model):
    __tablename__ = "third-party-accounts"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(32))      # github/qq/wechat
    openid = db.Column(db.String(128))        # 唯一标识
    unionid = db.Column(db.String(128))       # 跨应用统一标识
    nickname = db.Column(db.String(64))       # 昵称快照
    avatar = db.Column(db.String(255))        # 头像快照
    raw_profile = db.Column(db.JSON)          # 原始资料
    created_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
```

### 配置说明

在 `.env` 文件中配置 OAuth 凭证：

```bash
# GitHub OAuth（示例）
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:5173/auth/oauth/github/callback

# QQ OAuth
QQ_CLIENT_ID=your_qq_client_id
QQ_CLIENT_SECRET=your_qq_client_secret
QQ_REDIRECT_URI=http://localhost:5173/auth/oauth/qq/callback
```

**重要**：`REDIRECT_URI` 需要与第三方平台的回调配置完全一致。

## 前端实现

### 文件修改

1. **API 模块** (`frontend/src/api/auth/authApi.js`)

添加了两个新方法：
```javascript
getOAuthProviders() {
  return $http.get(`${url_prefix}/oauth/providers`);
},
oauthLogin(provider, redirectUrl) {
  const params = redirectUrl ? { redirect_url: redirectUrl } : {};
  return $http.get(`${url_prefix}/oauth/${provider}/login`, { params });
},
```

2. **登录页组件** (`frontend/src/views/login/LoginPage.vue`)

主要功能：
- 登录时自动加载可用的 OAuth 平台列表
- 动态渲染第三方登录按钮
- 使用弹窗方式打开 OAuth 授权页面
- 通过 `postMessage` 接收登录结果

### 使用流程

1. 用户在登录页面点击"GitHub 登录"按钮
2. 前端打开弹窗，跳转到 GitHub 授权页面
3. 用户授权后，GitHub 重定向到后端回调接口
4. 后端处理回调，创建/更新用户并生成 JWT tokens
5. 后端返回 HTML 页面，通过 `postMessage` 发送 tokens 给父窗口
6. 前端接收消息，保存 tokens 并跳转到首页

## 扩展新平台

### 后端配置

1. 在 `.env` 中添加平台凭证：
```bash
NEWPLATFORM_CLIENT_ID=your_client_id
NEWPLATFORM_CLIENT_SECRET=your_client_secret
NEWPLATFORM_REDIRECT_URI=http://localhost:5173/auth/oauth/newplatform/callback
```

2. 在 `third_party_login.py` 的 `OAUTH_CONFIGS` 中添加配置：
```python
"newplatform": {
    "client_id": os.getenv("NEWPLATFORM_CLIENT_ID", ""),
    "client_secret": os.getenv("NEWPLATFORM_CLIENT_SECRET", ""),
    "redirect_uri": os.getenv("NEWPLATFORM_REDIRECT_URI", ""),
},
```

完成！无需修改其他代码。

### 前端

前端会自动读取新增的平台配置并显示登录按钮。

## 数据库迁移

如果 `ThirdPartyAccount` 表还不存在，需要创建迁移：

```bash
cd backend
flask db migrate -m "添加第三方账号表"
flask db upgrade
```

## 支持的平台

目前已配置支持的平台（需要在 `.env` 中填写凭证）：

- ✅ GitHub
- ✅ Gitee
- ✅ QQ
- ✅ 微信
- ✅ 微信开放平台
- ✅ Google
- ✅ 新浪微博
- ✅ 钉钉
- ✅ Facebook
- ✅ 百度
- ✅ 飞书
- ✅ LinkedIn
- ✅ Microsoft
- ✅ 抖音
- ✅ Twitter

## 安全注意事项

1. **密钥保护**：`.env` 文件不应提交到版本控制系统
2. **HTTPS**：生产环境必须使用 HTTPS
3. **回调 URL**：确保回调 URL 白名单配置正确
4. **Token 存储**：使用 localStorage 时注意 XSS 防护

## 常见问题

### Q: 回调地址应该填什么？

A: 开发环境通常是 `http://localhost:5173/auth/oauth/<provider>/callback`，生产环境需要使用实际域名。

### Q: 如何测试 OAuth 登录？

A:
1. 在对应的第三方平台创建应用，获取 Client ID 和 Secret
2. 配置回调地址
3. 在 `.env` 中填写凭证
4. 重启后端服务

### Q: 用户已存在会怎样？

A: 系统会更新第三方账号快照（昵称、头像），并关联已存在的用户。

### Q: unionid 是用来做什么的？

A: 用于跨应用账号合并。目前仅预留字段，不自动合并逻辑。

## 技术栈

- 后端：Flask + senweaver-oauth + Flask-JWT-Extended
- 前端：Vue 3 + Element Plus
- 数据库：MySQL

## 参考

- [senweaver-oauth 文档](https://github.com/senweaver/senweaver-oauth)
- [OAuth 2.0 规范](https://oauth.net/2/)
