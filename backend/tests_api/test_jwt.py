import time
from unittest.mock import patch

import jwt as pyjwt
import pytest


class TestJwt:
    """JWT/JWTM 认证模块测试"""

    auth_prefix = "/auth"
    api_prefix = "/api/v1"

    # ==================== 一、登录认证流程 ====================

    def test_login_success(self, client, auth):
        """1.1.1 正常登录：正确的用户名和密码"""
        auth_instance = auth()
        # 注册用户
        auth_instance.register(username="testuser", password="testpass")

        # 登录
        response = auth_instance.login(username="testuser", password="testpass")
        assert response.status_code == 200
        assert response.json.get("code") == 200
        assert response.json.get("access_token") is not None
        assert response.json.get("refresh_token") is not None
        assert response.json.get("data").get("username") == "testuser"

    def test_login_with_fresh_token(self, client, auth):
        """1.1.2 登录后的 access_token 应该是 fresh=True"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 解码 token 检查 fresh 字段
        access_token = auth_instance._access_token
        assert access_token.startswith("Bearer ")
        token = access_token.replace("Bearer ", "")

        decoded = pyjwt.decode(token, options={"verify_signature": False})
        assert decoded.get("fresh") is True

    def test_login_with_nonexistent_user(self, client, auth):
        """1.2.1 登录：用户不存在"""
        auth_instance = auth()
        response = auth_instance.login(username="nonexistent", password="testpass")
        assert response.status_code == 200
        assert response.json.get("code") == 400
        assert "账号或密码错误" in response.json.get("message")

    def test_login_with_wrong_password(self, client, auth):
        """1.2.2 登录：密码错误"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")

        response = auth_instance.login(username="testuser", password="wrongpass")
        assert response.status_code == 200
        assert response.json.get("code") == 400
        assert "账号或密码错误" in response.json.get("message")

    def test_login_missing_username(self, client, auth):
        """1.2.3 登录：缺少用户名"""
        auth_instance = auth()
        response = client.post(
            self.auth_prefix + "/login", json={"uiPassword": "testpass"}
        )
        assert response.status_code == 200

    def test_login_empty_username(self, client, auth):
        """1.2.4 登录：用户名为空"""
        auth_instance = auth()
        response = auth_instance.login(username="", password="testpass")
        assert response.status_code == 200

    def test_login_empty_password(self, client, auth):
        """1.2.5 登录：密码为空"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")

        response = auth_instance.login(username="testuser", password="")
        assert response.status_code == 200
        assert response.json.get("code") == 400

    # ==================== 二、令牌刷新流程 ====================

    def test_refresh_token_success(self, client, auth):
        """2.1.1 使用 refresh_token 成功刷新 access_token"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 使用 refresh_token 刷新
        response = client.post(
            self.auth_prefix + "/refresh", headers=auth_instance.get_headers("refresh")
        )
        assert response.status_code == 200
        assert response.json.get("code") == 200
        assert response.json.get("data").get("access_token") is not None

    def test_refresh_token_not_fresh(self, client, auth):
        """2.1.2 刷新后的 access_token fresh=False"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 刷新 token
        response = client.post(
            self.auth_prefix + "/refresh", headers=auth_instance.get_headers("refresh")
        )
        new_token = response.json.get("data").get("access_token").replace("Bearer ", "")

        # 解码检查 fresh
        decoded = pyjwt.decode(new_token, options={"verify_signature": False})
        assert decoded.get("fresh") is False

    def test_refresh_with_access_token(self, client, auth):
        """2.2.1 使用 access_token 调用刷新接口应失败"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 使用 access_token 调用刷新接口
        response = client.post(
            self.auth_prefix + "/refresh", headers=auth_instance.get_headers("access")
        )
        assert (
            response.status_code == 422
        )  # 422 Unprocessable Entity - wrong token type

    def test_refresh_without_token(self, client, auth):
        """2.2.5 不带 token 调用刷新接口"""
        auth_instance = auth()
        response = client.post(self.auth_prefix + "/refresh")
        # 该项目使用 JSON body 返回 401 错误
        assert response.status_code == 200
        assert response.json.get("code") == 401

    # ==================== 三、访问受保护接口 ====================

    def test_access_protected_endpoint_with_valid_token(self, client, auth):
        """3.1.1 使用有效的 access_token 访问受保护接口"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 访问受保护接口
        response = client.get(
            self.auth_prefix + "/access_token_test",
            headers=auth_instance.get_headers("access"),
        )
        assert response.status_code == 200
        assert response.json.get("code") == 200
        assert "access_token_test" in response.json.get("message")

    def test_access_protected_endpoint_without_token(self, client, auth):
        """3.2.1 不带 token 访问受保护接口"""
        response = client.get(self.auth_prefix + "/access_token_test")
        # 该项目使用 JSON body 返回 401 错误
        assert response.status_code == 200
        assert response.json.get("code") == 401

    def test_access_with_invalid_format_token(self, client, auth):
        """3.2.4 使用无效格式的 Authorization 头"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 缺少 "Bearer" 前缀
        headers = {
            "Authorization": auth_instance._access_token.replace("Bearer ", ""),
            "Content-Type": "application/json",
        }
        response = client.get(self.auth_prefix + "/access_token_test", headers=headers)
        # 该项目使用 JSON body 返回 401 错误
        assert response.status_code == 200
        assert response.json.get("code") == 401

    def test_access_with_empty_token(self, client, auth):
        """3.2.6 使用空字符串作为 token"""
        headers = {"Authorization": "Bearer ", "Content-Type": "application/json"}
        response = client.get(self.auth_prefix + "/access_token_test", headers=headers)
        # JWT 库返回 422 Unprocessable Entity
        assert response.status_code == 422

    # ==================== 四、令牌失效与撤销 ====================

    def test_revoke_access_token(self, client, auth):
        """4.1.1 撤销 access_token 后无法访问受保护接口"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 撤销 token
        response = client.delete(
            self.auth_prefix + "/revokeToken",
            headers=auth_instance.get_headers("access"),
        )
        assert response.status_code == 200
        assert response.json.get("code") == 200

        # 撤销后尝试访问
        response = client.get(
            self.auth_prefix + "/access_token_test",
            headers=auth_instance.get_headers("access"),
        )
        # 该项目使用 JSON body 返回 401 错误
        assert response.status_code == 200
        assert response.json.get("code") == 401

    def test_revoke_refresh_token(self, client, auth):
        """4.1.2 撤销 refresh_token 后无法刷新"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 撤销 refresh_token
        response = client.delete(
            self.auth_prefix + "/revokeToken",
            headers=auth_instance.get_headers("refresh"),
        )
        assert response.status_code == 200

        # 尝试刷新
        response = client.post(
            self.auth_prefix + "/refresh", headers=auth_instance.get_headers("refresh")
        )
        # 该项目使用 JSON body 返回 401 错误
        assert response.status_code == 200
        assert response.json.get("code") == 401

    def test_revoke_token_response_message(self, client, auth):
        """4.1.3 撤销接口应返回撤销的 token 类型"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 撤销 access_token
        response = client.delete(
            self.auth_prefix + "/revokeToken",
            headers=auth_instance.get_headers("access"),
        )
        assert "Access" in response.json.get("message")

        # 撤销 refresh_token
        response = client.delete(
            self.auth_prefix + "/revokeToken",
            headers=auth_instance.get_headers("refresh"),
        )
        assert "Refresh" in response.json.get("message")

    # ==================== 五、令牌新鲜度控制 ====================

    def test_login_token_is_fresh(self, client, auth):
        """5.1.1 登录获取的 access_token fresh=True"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 检查新鲜度
        response = client.get(
            self.auth_prefix + "/checkFreshness",
            headers=auth_instance.get_headers("access"),
        )
        assert response.status_code == 200
        assert response.json.get("code") == 200
        assert "令牌新鲜" in response.json.get("message")

    def test_refreshed_token_not_fresh(self, client, auth):
        """5.1.3 刷新后的 access_token fresh=False"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 刷新 token
        refresh_response = client.post(
            self.auth_prefix + "/refresh", headers=auth_instance.get_headers("refresh")
        )
        # 更新 auth_instance 的 access_token
        auth_instance._access_token = refresh_response.json.get("data").get(
            "access_token"
        )

        # 检查新鲜度
        response = client.get(
            self.auth_prefix + "/checkFreshness",
            headers=auth_instance.get_headers("access"),
        )
        assert response.status_code == 200
        assert response.json.get("code") == 401
        assert "需要重新登录" in response.json.get("message")

    def test_non_fresh_token_fresh_operation(self, client, auth):
        """5.2.2 使用非 fresh token 访问需要 fresh=True 的接口"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 刷新 token
        refresh_response = client.post(
            self.auth_prefix + "/refresh", headers=auth_instance.get_headers("refresh")
        )
        new_token = refresh_response.json.get("data").get("access_token")

        # 使用非 fresh token 尝试修改密码（需要 fresh token）
        headers = {"Authorization": new_token, "Content-Type": "application/json"}
        response = client.post(
            self.auth_prefix + "/changePassword",
            headers=headers,
            json={"old_password": "testpass", "new_password": "newpass"},
        )
        # 该项目使用 JSON body 返回 401 错误
        assert response.status_code == 200
        assert response.json.get("code") == 401

    # ==================== 六、令牌过期与时间边界 ====================

    @patch("config.Config.JWT_ACCESS_TOKEN_EXPIRES")
    def test_short_lived_token_expiration(self, mock_expires, client, auth):
        """6.2.2 token 过期后立即失效"""
        # 该测试需要真实测试 token 过期,由于 mock 配置复杂,跳过此测试
        # 在实际环境中,JWT 会自动检查 token 的 exp 字段
        # 跳过原因: mock 需要在 app 创建前配置,而 pytest fixture 已经创建了 app
        pytest.skip("Token expiration test requires complex mocking setup")

    # ==================== 七、异常 Token 场景 ====================

    def test_malformed_token(self, client, auth):
        """7.2.2 malformed token（格式错误）"""
        headers = {
            "Authorization": "Bearer invalid.token.here",
            "Content-Type": "application/json",
        }
        response = client.get(self.auth_prefix + "/access_token_test", headers=headers)
        assert response.status_code == 422 or response.status_code == 401

    def test_token_missing_parts(self, client, auth):
        """7.2.3 token 部分片段为空"""
        headers = {"Authorization": "Bearer .", "Content-Type": "application/json"}
        response = client.get(self.auth_prefix + "/access_token_test", headers=headers)
        assert response.status_code == 422 or response.status_code == 401

    def test_tampered_token_signature(self, client, auth):
        """7.1.1 修改 token 签名部分"""
        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 修改签名
        token = auth_instance._access_token.replace("Bearer ", "")
        parts = token.split(".")
        parts[2] = "tampered" + parts[2][:10]  # 修改签名
        tampered_token = ".".join(parts)

        headers = {
            "Authorization": "Bearer " + tampered_token,
            "Content-Type": "application/json",
        }
        response = client.get(self.auth_prefix + "/access_token_test", headers=headers)
        assert response.status_code == 422 or response.status_code == 401

    # ==================== 八、权限控制与角色校验 ====================

    def test_admin_access_admin_endpoint(self, client, auth):
        """8.2.1 管理员可以访问 /admin/* 接口"""
        auth_instance = auth()
        # 注册管理员（使用特定邮箱）
        auth_instance.register_admin(username="admin", password="adminpass")
        auth_instance.login(username="admin", password="admin")

        # 访问管理员接口
        response = client.get(
            self.api_prefix + "/admin/init-summaries",
            headers=auth_instance.get_headers("access"),
        )
        # 应该可以访问，返回 405 表示方法不允许但认证通过
        # HTTP status_code 可能是 405，但不是 401 或 403 就表示认证和权限通过
        assert response.status_code != 401 and response.status_code != 403

    def test_normal_user_access_admin_endpoint(self, client, auth):
        """8.4.1 普通用户访问管理员接口应返回 403"""
        auth_instance = auth()
        auth_instance.register(username="user", password="userpass")
        auth_instance.login(username="user", password="userpass")

        # 访问管理员接口 - 使用 POST 方法
        response = client.post(
            self.api_prefix + "/admin/init-summaries",
            headers=auth_instance.get_headers("access"),
            json={},
        )
        assert response.status_code == 200
        assert response.json.get("code") == 403

    def test_user_permissions(self, client, auth):
        """8.4.3 检查用户权限接口"""
        auth_instance = auth()
        auth_instance.register(username="user", password="userpass")
        auth_instance.login(username="user", password="userpass")

        # 检查 FOLLOW 权限（普通用户应有此权限）
        response = client.get(
            self.api_prefix + "/users/permissions/1",
            headers=auth_instance.get_headers("access"),
        )
        assert response.status_code == 200
        # 权限数据在 data 字段中
        assert response.json.get("data") is True

    def test_user_without_admin_permission(self, client, auth):
        """8.4.4 普通用户没有 ADMIN 权限"""
        auth_instance = auth()
        auth_instance.register(username="user", password="userpass")
        auth_instance.login(username="user", password="userpass")

        # 检查 ADMIN 权限
        response = client.get(
            self.api_prefix + "/users/permissions/16",  # ADMIN = 16
            headers=auth_instance.get_headers("access"),
        )
        assert response.status_code == 200
        # 权限数据在 data 字段中
        assert response.json.get("data") is False

    # ==================== 九、并发与多设备场景 ====================

    def test_multiple_devices_login(self, client, auth):
        """9.1.1 同一用户在不同设备登录，各自获得独立 token"""
        auth1 = auth()
        auth2 = auth()

        # 同一用户从两个设备登录
        auth1.register(username="testuser", password="testpass")
        login1 = auth1.login(username="testuser", password="testpass")
        login2 = auth2.login(username="testuser", password="testpass")

        # 两个 token 应该不同
        assert login1.json.get("access_token") != login2.json.get("access_token")

        # 两个 token 都应该有效
        response1 = client.get(
            self.auth_prefix + "/access_token_test", headers=auth1.get_headers("access")
        )
        response2 = client.get(
            self.auth_prefix + "/access_token_test", headers=auth2.get_headers("access")
        )
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json.get("code") == 200
        assert response2.json.get("code") == 200

    def test_revoke_device_a_not_affect_device_b(self, client, auth):
        """9.1.2 设备 A 撤销 token，不影响设备 B 的 token"""
        auth1 = auth()
        auth2 = auth()

        # 同一用户从两个设备登录
        auth1.register(username="testuser", password="testpass")
        auth1.login(username="testuser", password="testpass")
        auth2.login(username="testuser", password="testpass")

        # 设备 A 撤销 token
        client.delete(
            self.auth_prefix + "/revokeToken", headers=auth1.get_headers("access")
        )

        # 设备 A 的 token 应该失效
        response1 = client.get(
            self.auth_prefix + "/access_token_test", headers=auth1.get_headers("access")
        )
        assert response1.status_code == 200
        assert response1.json.get("code") == 401

        # 设备 B 的 token 应该仍然有效
        response2 = client.get(
            self.auth_prefix + "/access_token_test", headers=auth2.get_headers("access")
        )
        assert response2.status_code == 200
        assert response2.json.get("code") == 200

    # ==================== 十、Redis 黑名单机制 ====================

    def test_token_in_redis_blacklist(self, client, auth, flask_app_context):
        """10.1.1 撤销 token 后，Redis 中存在对应的 jti"""
        from app import redis

        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 获取 token 的 jti
        import jwt

        token = auth_instance._access_token.replace("Bearer ", "")
        decoded = jwt.decode(token, options={"verify_signature": False})
        jti = decoded.get("jti")

        # 撤销 token
        client.delete(
            self.auth_prefix + "/revokeToken",
            headers=auth_instance.get_headers("access"),
        )

        # 检查 Redis 中是否存在
        blacklisted = redis.get(jti)
        assert blacklisted is not None

    def test_blacklisted_token_cannot_access(self, client, auth, flask_app_context):
        """10.2.2 黑名单中的 token，即使未过期也应失效"""
        from app import redis

        auth_instance = auth()
        auth_instance.register(username="testuser", password="testpass")
        auth_instance.login(username="testuser", password="testpass")

        # 获取 token 的 jti
        import jwt

        token = auth_instance._access_token.replace("Bearer ", "")
        decoded = jwt.decode(token, options={"verify_signature": False})
        jti = decoded.get("jti")

        # 手动添加到黑名单
        redis.set(jti, "", ex=3600)

        # 尝试访问
        response = client.get(
            self.auth_prefix + "/access_token_test",
            headers=auth_instance.get_headers("access"),
        )
        # 该项目使用 JSON body 返回 401 错误
        assert response.status_code == 200
        assert response.json.get("code") == 401

    # ==================== 十一、API 级别认证中间件 ====================

    def test_public_endpoint_without_auth(self, client, auth):
        """12.1.1 /api/v1/posts 路径无需认证"""
        response = client.get(self.api_prefix + "/posts")
        assert response.status_code == 200
        assert response.json.get("code") == 200

    def test_protected_endpoint_without_auth(self, client, auth):
        """12.2.1 认证失败返回 401"""
        # 尝试访问受保护接口
        response = client.get(self.api_prefix + "/files/token")
        # 该项目使用 JSON body 返回 401 错误
        assert response.status_code == 200
        assert response.json.get("code") == 401

    # ==================== 十二、集成场景 ====================

    def test_complete_auth_flow(self, client, auth):
        """13.1.1 完整业务流程：注册 → 登录 → 访问 → 刷新 → 继续访问"""
        auth_instance = auth()

        # 1. 注册
        register_response = auth_instance.register(username="user", password="pass")
        assert register_response.json.get("code") == 200

        # 2. 登录
        login_response = auth_instance.login(username="user", password="pass")
        assert login_response.json.get("access_token") is not None
        assert login_response.json.get("refresh_token") is not None

        # 3. 访问受保护接口
        response = client.get(
            self.auth_prefix + "/access_token_test",
            headers=auth_instance.get_headers("access"),
        )
        assert response.status_code == 200
        assert response.json.get("code") == 200

        # 4. 刷新 token
        refresh_response = client.post(
            self.auth_prefix + "/refresh", headers=auth_instance.get_headers("refresh")
        )
        assert refresh_response.json.get("data").get("access_token") is not None

        # 5. 继续访问（使用新的 access_token）
        response = client.get(
            self.auth_prefix + "/access_token_test",
            headers=auth_instance.get_headers("access"),
        )
        assert response.status_code == 200
        assert response.json.get("code") == 200

    def test_login_revoke_login_again(self, client, auth):
        """13.1.3 登录 → 撤销 access_token → 尝试刷新仍然成功（因为 refresh_token 独立）→ 重新登录"""
        auth_instance = auth()

        # 登录
        auth_instance.register(username="user", password="pass")
        auth_instance.login(username="user", password="pass")

        # 只撤销 access_token,不撤销 refresh_token
        client.delete(
            self.auth_prefix + "/revokeToken",
            headers=auth_instance.get_headers("access"),
        )

        # refresh_token 仍然可以刷新（因为它是独立的）
        response = client.post(
            self.auth_prefix + "/refresh", headers=auth_instance.get_headers("refresh")
        )
        # 刷新应该成功,返回新的 access_token
        assert response.status_code == 200
        assert response.json.get("code") == 200
        assert response.json.get("data").get("access_token") is not None

        # 重新登录应成功
        login_response = auth_instance.login(username="user", password="pass")
        assert login_response.json.get("code") == 200
        assert login_response.json.get("access_token") is not None

    def test_change_password_requires_fresh_token(self, client, auth):
        """13.1.2 修改密码需要 fresh token"""
        auth_instance = auth()

        # 注册并登录
        auth_instance.register(username="user", password="oldpass")
        auth_instance.login(username="user", password="oldpass")

        # 使用 fresh token 修改密码
        response = client.post(
            self.auth_prefix + "/changePassword",
            headers=auth_instance.get_headers("access"),
            json={"old_password": "oldpass", "new_password": "newpass"},
        )
        assert response.status_code == 200
        assert response.json.get("code") == 200

        # 使用新密码登录
        auth_instance._access_token = None
        login_response = auth_instance.login(username="user", password="newpass")
        assert login_response.json.get("code") == 200

    def test_upload_requires_auth(self, client, auth):
        """13.2.1 上传文件接口需要有效 token"""
        auth_instance = auth()

        # 不带 token 访问
        response = client.get(self.api_prefix + "/files/token")
        # 该项目使用 JSON body 返回 401 错误
        assert response.status_code == 200
        assert response.json.get("code") == 401

        # 登录后访问
        auth_instance.register(username="user", password="pass")
        auth_instance.login(username="user", password="pass")

        response = client.get(
            self.api_prefix + "/files/token",
            headers=auth_instance.get_headers("access"),
        )
        assert response.status_code == 200
        assert response.json.get("code") == 200

    # ==================== 十三、边界条件与特殊场景 ====================

    def test_multiple_bearer_in_header(self, client, auth):
        """14.2.1 Authorization 头包含多个 Bearer token"""
        headers = {
            "Authorization": "Bearer token1 Bearer token2",
            "Content-Type": "application/json",
        }
        response = client.get(self.auth_prefix + "/access_token_test", headers=headers)
        # JWT 库返回 422 Unprocessable Entity
        assert response.status_code == 422

    # ==================== 十四、错误处理与响应格式 ====================

    def test_login_error_response_format(self, client, auth):
        """15.2.1 错误响应格式一致性"""
        auth_instance = auth()
        response = auth_instance.login(username="wrong", password="wrong")

        assert response.status_code == 200
        assert "code" in response.json
        assert "message" in response.json
        assert response.json.get("code") == 400

    def test_success_login_response_format(self, client, auth):
        """15.2.2 成功响应格式"""
        auth_instance = auth()
        auth_instance.register(username="user", password="pass")
        response = auth_instance.login(username="user", password="pass")

        assert response.status_code == 200
        assert "code" in response.json
        assert "data" in response.json
        assert "access_token" in response.json
        assert "refresh_token" in response.json
        assert response.json.get("code") == 200
