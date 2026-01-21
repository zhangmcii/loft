# OAuth 第三方登录流程说明

## 总体流程

```
用户点击登录按钮
     ↓
前端跳转到后端 /auth/oauth/<provider>/login
     ↓
后端重定向到第三方平台授权页面
     ↓
用户在第三方平台授权
     ↓
第三方平台重定向到后端 /auth/oauth/<provider>/callback
     ↓
后端重定向到前端 /oauth/callback/<provider>?code=xxx&state=xxx
     ↓
前端回调页面加载，显示加载动画
     ↓
前端调用后端 API /auth/oauth/<provider>/callback-api?code=xxx&state=xxx
     ↓
后端处理授权，生成 JWT tokens，返回用户信息
     ↓
前端保存 tokens，跳转到首页
```

## 详细步骤

### 1. 前端发起登录

**登录页面** (`LoginPage.vue`)

用户点击第三方登录按钮：
```javascript
handleOAuthLogin(provider) {
  ElMessage.info(`正在跳转到 ${provider} 授权页面...`);
  window.location.href = `/auth/oauth/${provider}/login`;
}
```

### 2. 后端重定向到第三方平台

**后端接口** (`/auth/oauth/<provider>/login`)

```python
@auth.route("/oauth/<provider>/login", methods=["GET"])
def oauth_login_route(provider):
    """OAuth 登录 - 重定向到第三方授权页面"""
    return oauth_login(provider)
```

后端使用 `senweaver-oauth` 构建授权 URL，然后重定向用户到第三方平台。

### 3. 第三方平台授权

用户在第三方平台（如 GitHub）完成授权后，第三方平台会重定向到后端回调地址。

### 4. 后端处理回调并重定向到前端

**后端接口** (`/auth/oauth/<provider>/callback`)

```python
@auth.route("/oauth/<provider>/callback", methods=["GET"])
def oauth_callback_route(provider):
    """OAuth 回调 - 重定向到前端回调页面"""
    # 重定向到前端回调页面，带上所有查询参数
    callback_url = f"/oauth/callback/{provider}?{request.query_string.decode()}"
    return redirect(callback_url)
```

**注意**：此接口不处理登录逻辑，只是将用户重定向到前端回调页面，带上所有授权参数。

### 5. 前端回调页面处理授权

**前端回调页面** (`/oauth/callback/:provider`)

页面加载时：
1. 显示友好的加载动画
2. 从 URL 中提取授权参数
3. 调用后端 API 完成登录

```vue
onMounted(async () => {
  const providerParam = route.params.provider;
  const queryParams = route.query;

  // 调用后端接口处理回调
  const res = await authApi.oauthCallback(providerParam, queryParams);

  if (res.code === 200 && res.data) {
    const { user, access_token, refresh_token } = res.data;

    currentUser.setUserInfo(user);
    currentUser.access_token = access_token;
    currentUser.refresh_token = refresh_token;

    setTimeout(() => {
      router.push('/posts');
    }, 500);
  } else {
    error.value = res.message || '登录失败，请重试';
  }
});
```

### 6. 后端 API 处理登录

**后端接口** (`/auth/oauth/<provider>/callback-api`)

```python
@auth.route("/oauth/<provider>/callback-api", methods=["GET"])
def oauth_callback_api_route(provider):
    """OAuth 回调 API - 前端回调页面调用此接口处理登录"""
    from .third_party_login import oauth_callback_api
    return oauth_callback_api(provider)
```

处理逻辑：
1. 接收授权参数（code、state 等）
2. 使用 `senweaver-oauth` 获取用户信息
3. 查询或创建用户
4. 生成 JWT tokens
5. 返回用户信息和 tokens

```python
def oauth_callback_api(provider: str):
    """OAuth 回调 API 接口"""
    callback_params = dict(request.args)

    # 处理 OAuth 回调
    success_flag, data, error_msg = handle_oauth_callback(provider, callback_params)

    if not success_flag:
        return error(code=400, message=error_msg)

    # 登录成功，返回 tokens 和用户信息
    return success(data=data)
```

### 7. 前端保存登录状态

成功后：
1. 保存 tokens 到 Pinia store
2. 保存用户信息
3. 跳转到首页

失败后：
1. 显示错误信息
2. 提供返回登录页的按钮

## 优势

### 1. 用户体验友好

- 前端回调页面有精美的加载动画
- 成功/失败状态清晰展示
- 自动跳转，减少用户操作

### 2. 代码结构清晰

- 后端只负责业务逻辑（OAuth 处理、用户创建、token 生成）
- 前端负责页面展示和交互
- 职责分离，易于维护

### 3. 前后端分离

- 后端返回纯 JSON，不涉及前端页面渲染
- 前端完全控制 UI 展示
- 符合前后端分离架构

### 4. 易于调试

- 可以通过浏览器开发者工具查看完整的网络请求
- 前端错误容易定位
- 后端日志清晰

## URL 设计

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/oauth/providers` | GET | 获取可用的 OAuth 平台列表 |
| `/auth/oauth/<provider>/login` | GET | 发起 OAuth 登录，重定向到第三方 |
| `/auth/oauth/<provider>/callback` | GET | 接收第三方回调，重定向到前端 |
| `/auth/oauth/<provider>/callback-api` | GET | 前端回调页调用，完成登录 |
| `/oauth/callback/:provider` | - | 前端路由，显示回调页面 |

## 安全考虑

1. **回调地址验证**：确保只有授权的第三方平台可以调用回调
2. **Token 存储**：使用 Pinia + localStorage 持久化，注意 XSS 防护
3. **HTTPS**：生产环境必须使用 HTTPS
4. **CSRF 保护**：使用 state 参数防止 CSRF 攻击（`senweaver-oauth` 已处理）

## 错误处理

### 常见错误

1. **平台未配置**
   - 检查 `.env` 中是否有对应的 `CLIENT_ID` 和 `CLIENT_SECRET`

2. **授权失败**
   - 检查回调地址是否正确
   - 检查 Client Secret 是否正确

3. **用户信息获取失败**
   - 检查第三方平台的 API 权限配置
   - 查看后端日志获取详细错误

### 前端错误展示

回调页面会展示不同的状态：

- **加载中**：显示加载动画
- **成功**：显示成功图标，自动跳转
- **失败**：显示错误信息和返回按钮
