# GitHub OAuth 登录配置示例

本文档演示如何配置 GitHub OAuth 登录。

## 步骤 1：创建 GitHub OAuth App

1. 访问 https://github.com/settings/developers
2. 点击 "OAuth Apps" -> "New OAuth App"
3. 填写应用信息：
   - **Application name**: 你的应用名称（例如：我的博客）
   - **Homepage URL**: `http://localhost:5173`（开发环境）
   - **Application description**: （可选）
   - **Authorization callback URL**: `http://localhost:5173/auth/oauth/github/callback`

4. 点击 "Register application"
5. 记录生成的 **Client ID**
6. 点击 "Generate a new client secret"，生成后记录 **Client Secret**

## 步骤 2：配置后端环境变量

在 `backend/.env` 文件中添加：

```bash
# GitHub OAuth
GITHUB_CLIENT_ID=Iv1xxxxxxxxxxxxxxxxx
GITHUB_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_REDIRECT_URI=http://localhost:5173/auth/oauth/github/callback
```

## 步骤 3：测试配置

运行测试脚本：

```bash
cd backend
python test_oauth_config.py
```

应该看到输出：

```
可用的 OAuth 提供商（共 1 个）：
------------------------------------------------------------
✅ GitHub (github)
   - Client ID: Iv1xxxxxxxxxxxxxxxxx...
   - Redirect URI: http://localhost:5173/auth/oauth/github/callback
```

## 步骤 4：启动服务

启动后端服务：

```bash
cd backend
flask run --host=0.0.0.0 --port=8082
```

启动前端服务：

```bash
cd frontend
npm run dev
```

## 步骤 5：测试登录

1. 访问 http://localhost:5173/login
2. 在登录页面应该能看到 "GitHub" 登录按钮
3. 点击按钮，打开 GitHub 授权弹窗
4. 授权成功后，会自动登录并跳转到首页

## 常见问题

### Q: 点击登录按钮没有反应？

A: 检查以下几点：
1. 浏览器是否拦截了弹窗，允许该网站的弹窗
2. 后端服务是否正常运行
3. `/auth/oauth/providers` 接口是否返回了 GitHub 配置

### Q: 授权后报错 "平台 github 未正确配置"？

A: 检查：
1. `.env` 文件中的 GITHUB_CLIENT_ID 和 GITHUB_CLIENT_SECRET 是否正确填写
2. 是否重启了后端服务（修改 .env 后需要重启）

### Q: 授权后显示 "获取用户信息失败"？

A: 可能原因：
1. Client Secret 错误
2. 回调地址配置不一致
3. GitHub OAuth App 配置有问题

检查后端日志查看详细错误信息。

### Q: 首次登录后用户名是什么？

A: 首次登录时，系统会自动创建用户，用户名格式为：`github_<openid前8位>`

例如：`github_a1b2c3d4`

如果用户名重复，会自动添加数字后缀。

### Q: 如何关联已有的本地账号？

A: 目前版本不支持账号绑定功能，每次使用 OAuth 登录都会创建新用户。

未来版本会添加"账号绑定"功能，允许将第三方账号关联到已有用户。

## 生产环境配置

生产环境需要使用 HTTPS：

1. 修改 `.env` 中的回调地址：
```bash
GITHUB_REDIRECT_URI=https://yourdomain.com/auth/oauth/github/callback
```

2. 在 GitHub OAuth App 设置中更新回调地址：
- Homepage URL: `https://yourdomain.com`
- Authorization callback URL: `https://yourdomain.com/auth/oauth/github/callback`

3. 配置 SSL 证书（Nginx/Apache 等）

## 其他平台配置

其他平台的配置流程类似：

| 平台 | 开发者平台入口 | 回调地址格式 |
|------|----------------|-------------|
| Gitee | https://gitee.com/oauth/applications | `http://localhost:5173/auth/oauth/gitee/callback` |
| QQ | https://connect.qq.com/ | `http://localhost:5173/auth/oauth/qq/callback` |
| 微信 | https://open.weixin.qq.com/ | `http://localhost:5173/auth/oauth/wechat/callback` |
| Google | https://console.cloud.google.com/apis/credentials | `http://localhost:5173/auth/oauth/google/callback` |

详细配置请参考对应平台的官方文档。
