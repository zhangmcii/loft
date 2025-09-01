from base64 import b64encode


class TestUserProfileCase:
    """测试用户资料相关功能"""
    pre_fix = '/api/v1'

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode((username + ":" + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }

    def test_get_user_profile(self, client, auth):
        """测试获取用户资料"""
        # 注册并登录用户
        auth.register()
        auth.login()

        # 获取当前用户信息
        r = client.get(self.pre_fix + '/users/1', headers=auth.get_headers())
        assert r.status_code == 200
        assert r.json.get('code') == 200
        assert r.json.get('data').get('username') == 'test'

        # 获取不存在的用户信息
        r = client.get(self.pre_fix + '/users/999', headers=auth.get_headers())
        assert r.json.get('code') == 404

    def test_update_user_profile(self, client, auth):
        """测试更新用户资料"""
        # 注册并登录用户
        auth.register()
        auth.login()

        # 更新用户资料
        update_data = {
            'nickname': '测试昵称',
        }
        r = client.patch(self.pre_fix + '/users/1', headers=auth.get_headers(), json=update_data)
        assert r.status_code == 200
        assert r.json.get('code') == 200
        assert "用户资料更新成功" in r.json.get('message')

        # 验证更新是否成功
        r = client.get(self.pre_fix + '/users/1', headers=auth.get_headers())
        assert r.status_code == 200
        assert r.json.get('data').get('nickname') == '测试昵称'

    def test_follow_unfollow_user(self, client, auth):
        """测试关注和取消关注用户"""
        # 注册第一个用户
        auth.register(username='user1', password='password1')
        auth.login(username='user1', password='password1')
        headers_user1 = auth.get_headers()

        # 注册第二个用户
        auth.register(username='user2', password='password2')
        auth.login(username='user2', password='password2')
        headers_user2 = auth.get_headers()

        # 获取用户ID
        r = client.get(self.pre_fix + '/users/1', headers=headers_user1)
        user1_id = r.json.get('data').get('id')
        username1 = r.json.get('data').get('username')

        r = client.get(self.pre_fix + '/users/2', headers=headers_user2)
        user2_id = r.json.get('data').get('id')
        username2 = r.json.get('data').get('username')

        # user2 关注 user1
        r = client.post(self.pre_fix + f'/users/{username1}/follow', headers=headers_user2)
        assert r.status_code == 200
        assert r.json.get('code') == 200

        # 验证关注状态
        r = client.get(self.pre_fix + f'/users/{user1_id}', headers=headers_user2)
        assert r.json.get('data').get('is_followed_by_current_user') == True

        # user2 取消关注 user1
        r = client.delete(self.pre_fix + f'/users/{username1}/follow', headers=headers_user2)
        assert r.status_code == 200
        assert r.json.get('code') == 200

        # 验证取消关注状态
        r = client.get(self.pre_fix + f'/users/{user1_id}', headers=headers_user2)
        assert r.json.get('data').get('is_followed_by_current_user') == False
