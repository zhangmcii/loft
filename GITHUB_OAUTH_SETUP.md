# GitHub OAuth 登录配置指南

## 功能说明

本项目已集成 GitHub OAuth 第三方登录功能，允许用户通过 GitHub 账号登录。

## 实现内容

### 后端部分

1. **文件**: `backend/app/auth/third_party_login.py`
   - 提供 GitHub OAuth 授权流程
   - 端点:
     - `GET /auth/bp/github/authorize` - 获取 GitHub 授权 URL
     - `GET /auth/bp/github/callback` - 处理 GitHub OAuth 回调

2. **数据库交互**:
   - 使用 `ThirdPartyAccount` 表存储第三方账号信息
   - 使用 `User` 表存储用户信息
   - 首次登录自动创建用户，后续登录更新快照信息

3. **GitHub 用户信息映射**:
   - `openid`: GitHub 用户 ID（字符串形式）
   - `unionid`: None（GitHub 无此概念）
   - `nickname`: GitHub 显示名称
   - `avatar`: GitHub 头像 URL
   - `email`: GitHub 邮箱（如公开）

### 前端部分

1. **文件**: `frontend/src/views/login/LoginPage.vue`
   - 新增「GitHub 登录」按钮
   - 点击后调用后端获取授权 URL 并跳转

2. **文件**: `frontend/src/views/login/GitHubCallback.vue`
   - 处理 GitHub OAuth 回调
   - 自动登录并跳转到原页面

3. **文件**: `frontend/src/api/auth/authApi.js`
   - 新增 `getGitHubAuthUrl()` 方法

## 配置步骤

### 1. 创建 GitHub OAuth App

1. 访问 [GitHub Developer Settings](https://github.com/settings/developers)
2. 点击「OAuth Apps」→「New OAuth App」
3. 填写应用信息:
   - **Application name**: 你的应用名称（如 "云端阁楼"）
   - **Homepage URL**: `http://127.0.0.1:5173`（开发环境）
   - **Authorization callback URL**: `http://127.0.0.1:5173/callback/github`（必须与 `GITHUB_REDIRECT_URI` 一致）
4. 创建后，记录 `Client ID` 和 `Client Secret`

### 2. 配置后端环境变量

编辑 `backend/.env` 文件:

```env
# GitHub OAuth 配置
GITHUB_CLIENT_ID=your_actual_github_client_id_here
GITHUB_CLIENT_SECRET=your_actual_github_client_secret_here
# 前端回调地址，需在 GitHub OAuth App 中配置
GITHUB_REDIRECT_URI=http://127.0.0.1:5173/callback/github
```

### 3. 生产环境配置

生产环境需要更新以下配置:

1. **GitHub OAuth App**:
   - Homepage URL: `https://your-domain.com`
   - Authorization callback URL: `https://your-domain.com/callback/github`

2. **后端 `.env`**:
   ```env
   GITHUB_REDIRECT_URI=https://your-domain.com/callback/github
   ```

3. **前端代码** (如需):
   - 修改 `GitHubCallback.vue` 中的 API 地址

## 使用流程

1. 用户点击登录页面的「GitHub 登录」按钮
2. 前端调用 `/auth/bp/github/authorize` 获取授权 URL
3. 跳转到 GitHub 授权页面
4. 用户授权后，GitHub 重定向回前端 `/callback/github?code=xxx`
5. 前端回调页面调用后端 `/auth/bp/github/callback?code=xxx`
6. 后端:
   - 使用 code 换取 access_token
   - 获取 GitHub 用户信息
   - 查询或创建用户和第三方账号记录
   - 返回 JWT token
7. 前端保存 token 并跳转到主页

## 数据库字段说明

### ThirdPartyAccount 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| provider | String(32) | 第三方平台（固定为 "github"） |
| openid | String(128) | GitHub 用户 ID |
| unionid | String(128) | 跨应用统一身份（GitHub 为 None） |
| nickname | String(64) | 用户昵称快照 |
| avatar | String(255) | 头像 URL 快照 |
| raw_profile | JSON | GitHub 原始用户信息 |
| created_at | DateTime | 创建时间 |
| user_id | Integer | 关联的用户 ID（外键） |

## 用户名生成规则

首次登录时，用户名自动生成:
- 格式: `gh_{github_login}`
- 如重复则添加数字后缀: `gh_johndoe2`, `gh_johndoe3`...

## 测试

1. 确保 Flask 后端和 Vue 前端都已启动
2. 访问登录页面
3. 点击「GitHub 登录」按钮
4. 完成授权流程
5. 验证是否成功登录

## 注意事项

1. **Callback URL 一致性**: GitHub OAuth App 配置的回调地址必须与后端 `GITHUB_REDIRECT_URI` 完全一致
2. **HTTPS**: 生产环境必须使用 HTTPS
3. **Client Secret 安全**: 不要将 `Client Secret` 提交到版本控制
4. **邮箱获取**: 部分用户可能未公开邮箱，此时 `email` 字段为 `null`
5. **已存在用户**: 同一 GitHub 账号重复登录会更新快照信息，但不会创建新用户

## 扩展其他平台

如需添加其他第三方登录平台（如 Gitee、微信等），参考 `third_party_login.py` 中的实现模式即可。
