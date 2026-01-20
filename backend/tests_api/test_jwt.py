class TestJwt:
    def test_revoke_access_token(self, client, auth):
        """ "撤销访问令牌"""
        auth_instance = auth()
        # 注册并验证成功
        register_response = auth_instance.register()
        assert register_response.status_code == 200
        assert register_response.json.get("code") == 200

        # 登录并验证成功
        login_response = auth_instance.login()
        assert login_response.status_code == 200
        assert login_response.json.get("code") == 200
        assert login_response.json.get("access_token") is not None

        # 撤销访问令牌
        logout_response = client.delete(
            "/auth/revokeToken",
            headers=auth_instance.get_headers(),
        )

        assert logout_response.status_code == 200
        assert logout_response.json.get("code") == 200
        assert (
            logout_response.json.get("message") == "Access token successfully revoked"
        )

        # 测试访问令牌
        expired_token_response = client.get(
            "/auth/access_token_test", headers=auth_instance.get_headers()
        )
        assert expired_token_response.status_code == 200
        assert expired_token_response.json.get("code") == 401
        assert expired_token_response.json.get("message") == "该token已被撤销"

    def test_revoke_refresh_token(self, client, auth):
        # 退出登陆时，撤销刷新令牌
        auth_instance = auth()
        # 注册并验证成功
        register_response = auth_instance.register()
        assert register_response.status_code == 200
        assert register_response.json.get("code") == 200

        # 登录并验证成功
        login_response = auth_instance.login()
        assert login_response.status_code == 200
        assert login_response.json.get("code") == 200
        assert login_response.json.get("access_token") is not None

        # 撤销刷新令牌
        logout_response = client.delete(
            "/auth/revokeToken",
            headers=auth_instance.get_headers("refresh"),
        )

        assert logout_response.status_code == 200
        assert logout_response.json.get("code") == 200
        assert (
            logout_response.json.get("message") == "Refresh token successfully revoked"
        )

        expired_token_response = client.get(
            "/auth/refresh_token_test", headers=auth_instance.get_headers("refresh")
        )
        assert expired_token_response.status_code == 200
        assert expired_token_response.json.get("code") == 401
        assert expired_token_response.json.get("message") == "该token已被撤销"
