# OAuth 第三方登录快速开始

本项目已集成第三方登录功能，支持 GitHub、Gitee、QQ、微信等多个平台。

## 快速开始（以 GitHub 为例）

### 1. 配置环境变量

编辑 `backend/.env` 文件，添加 GitHub OAuth 配置：

```bash
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:5173/auth/oauth/github/callback
```

### 2. 获取 GitHub OAuth 凭证

1. 访问 https://github.com/settings/developers
2. 创建 OAuth App，填写回调地址：`http://localhost:5173/auth/oauth/github/callback`
3. 复制 Client ID 和 Client Secret 到 `.env`

### 3. 重启后端服务

```bash
cd backend
flask run --host=0.0.0.0 --port=8082
```

### 4. 测试登录

访问 http://localhost:5173/login，点击 "GitHub" 登录按钮。

## 支持的平台

- GitHub ✅
- Gitee ✅
- QQ ✅
- 微信 ✅
- Google ✅
- 更多...（详见 `docs/OAUTH_README.md`）

## 扩展新平台

只需在 `.env` 中添加平台凭证，无需修改代码。

```bash
# 示例：添加 Gitee 登录
GITEE_CLIENT_ID=your_gitee_client_id
GITEE_CLIENT_SECRET=your_gitee_client_secret
GITEE_REDIRECT_URI=http://localhost:5173/auth/oauth/gitee/callback
```

## 技术架构

- 后端：Flask + senweaver-oauth
- 前端：Vue 3（弹窗 + postMessage）
- 数据库：MySQL（User + ThirdPartyAccount 表）

## 文档

- 详细文档：`docs/OAUTH_README.md`
- GitHub 配置示例：`docs/OAUTH_EXAMPLE.md`
- 测试脚本：`backend/test_oauth_config.py`

## 运行测试

```bash
cd backend
python test_oauth_config.py
```
