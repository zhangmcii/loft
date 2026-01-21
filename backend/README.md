## 第三方登录（Flask + Vue + senweaver-oauth）指南

### 目标
- 后端使用 `senweaver-oauth` 统一处理各平台 OAuth，按配置自动启用/关闭。
- 回调后落地到本地 `User` 与 `ThirdPartyAccount`，并签发 JWT。
- 前端动态渲染平台按钮，统一回调页接收登录结果。


### 关键环境变量（开发示例）
```
# GitHub
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
# 可选，未配置则后端自动生成
GITHUB_REDIRECT_URI=http://127.0.0.1:5000/auth/oauth/callback/github

# 前端回跳地址（必须与前端路由一致）
FRONTEND_OAUTH_REDIRECT=http://127.0.0.1:5173/oauth/callback
```

> GitHub 后台 OAuth 应用的 callback URL 需与 `GITHUB_REDIRECT_URI` 保持一致。

### 后端核心文件与接口
- `app/auth/third_party_login.py`
  - `GET /auth/oauth/providers`：返回已启用平台列表（由配置决定）。
  - `GET /auth/oauth/authorize/<provider>`：生成第三方授权 URL。
  - `GET /auth/oauth/callback/<provider>`：处理回调，写库并签发 JWT，随后重定向到前端。
- `OAUTH_CONFIGS` 中按平台填入 `client_id`/`client_secret`（缺失即视为未启用）。新增平台只需在此追加配置并补充环境变量，无需改流程。

### 数据库落地规则
- 查 `ThirdPartyAccount(provider, openid)`：
  - **不存在**：创建 `User`（昵称/头像取第三方，密码随机不可登录），再创建 `ThirdPartyAccount` 绑定 `user_id`。
  - **已存在**：更新 `nickname`、`avatar`、`raw_profile` 快照，复用已有 `user_id`。
- `unionid` 仅存储，不做自动合并。

### 前端流程（简述）
- 登录页加载时调用 `/auth/oauth/providers`，动态渲染按钮。
- 点击按钮后调 `/auth/oauth/authorize/<provider>` 获取授权链接并跳转第三方。
- 第三方回调 → 后端落地/签发 → 重定向到前端 `/oauth/callback`，附带 `access_token`、`refresh_token`、`user`（JSON）。
- 回调页写入 Pinia（与密码登录同存储），然后跳转业务页面。

### 新增平台步骤
1) 在 `.env` 添加对应 `CLIENT_ID` / `CLIENT_SECRET` / `REDIRECT_URI`。  
2) 在 `OAUTH_CONFIGS` 追加同结构配置（`display_name`、`client_id`、`client_secret`、`redirect_uri`）。  
3) 在第三方后台将回调地址设置为 `http(s)://<backend>/auth/oauth/callback/<provider>`。  
4) 前端无需改动，按钮自动出现。

### 常见问题
- **AttributeError: 'AuthSource' object has no attribute 'upper'**  
  已修复：统一传字符串 `source_name` 给 `AuthRequestBuilder`。
- **提示平台未配置**  
  确认环境变量 `client_id` / `client_secret` 非空，或检查 `OAUTH_CONFIGS` 键是否与 `provider` 路径一致。
