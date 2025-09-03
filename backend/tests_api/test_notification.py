from base64 import b64encode


class TestNotificationCase:
    """测试通知推送功能"""

    pre_fix = "/api/v1"

    def get_api_headers(self, username, password):
        return {
            "Authorization": "Basic "
            + b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
            "Accept": "application/json",
            "Content-type": "application/json",
        }

    def test_comment_notification(self, client, auth):
        """测试评论通知"""
        # 注册第一个用户并发布文章
        auth.register(username="author1", password="password")
        auth.login(username="author1", password="password")
        author_headers = auth.get_headers()

        # 发布文章
        r = client.post(
            self.pre_fix + "/posts",
            headers=author_headers,
            json={"body": "测试文章内容", "bodyHtml": "测试文章内容", "images": []},
        )
        assert r.json.get("code") == 200
        post_id = r.json.get("data")[0].get("id")

        # 注册第二个用户
        auth.register(username="commenter1", password="password")
        auth.login(username="commenter1", password="password")

        # 第二个用户评论第一个用户的文章
        r = client.post(
            self.pre_fix + f"/posts/{post_id}/comments",
            headers=auth.get_headers(),
            json={"body": "这是一条测试评论", "directParentId": None, "at": []},
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 第一个用户查看通知
        r = client.get(self.pre_fix + "/notifications", headers=author_headers)
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 验证通知内容
        notifications = r.json.get("data")
        assert len(notifications) > 0
        assert notifications[0].get("type") == "评论"
        assert notifications[0].get("triggerUsername") == "commenter1"

    def test_like_notification(self, client, auth):
        """测试点赞通知"""
        # 注册第一个用户并发布文章
        auth.register(username="author2", password="password")
        auth.login(username="author2", password="password")
        author_headers = auth.get_headers()

        # 发布文章
        r = client.post(
            self.pre_fix + "/posts",
            headers=author_headers,
            json={"body": "测试文章内容", "bodyHtml": "测试文章内容", "images": []},
        )
        assert r.json.get("code") == 200
        post_id = r.json.get("data")[0].get("id")

        # 注册第二个用户
        auth.register(username="liker2", password="password")
        auth.login(username="liker2", password="password")
        liker_headers = auth.get_headers()

        # 第二个用户点赞第一个用户的文章
        r = client.post(self.pre_fix + f"/posts/{post_id}/likes", headers=liker_headers)
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 第一个用户查看通知
        r = client.get(self.pre_fix + "/notifications", headers=author_headers)
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 验证通知内容
        notifications = r.json.get("data")

        assert len(notifications) > 0
        assert notifications[-1].get("type") == "点赞"
        assert notifications[-1].get("triggerUsername") == "liker2"

    def test_reply_notification(self, client, auth):
        """测试回复通知"""
        # 注册第一个用户并发布文章和评论
        auth.register(username="commenter3", password="password")
        auth.login(username="commenter3", password="password")
        commenter1_headers = auth.get_headers()

        # 发布文章
        r = client.post(
            self.pre_fix + "/posts",
            headers=commenter1_headers,
            json={"body": "测试文章内容", "bodyHtml": "测试文章内容", "images": []},
        )
        assert r.json.get("code") == 200
        post_id = r.json.get("data")[0].get("id")

        # 发表评论
        r = client.post(
            self.pre_fix + f"/posts/{post_id}/comments",
            headers=auth.get_headers(),
            json={"body": "这是一条评论", "directParentId": None, "at": []},
        )
        assert r.status_code == 200
        comment_id = r.json.get("data").get("id")

        # 注册第二个用户
        auth.register(username="commenter31", password="password")
        auth.login(username="commenter31", password="password")

        # 第二个用户回复第一个用户的评论
        r = client.post(
            self.pre_fix + f"/posts/{post_id}/comments",
            headers=auth.get_headers(),
            json={"body": "这是对评论的回复", "directParentId": comment_id, "at": []},
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 第一个用户查看通知
        r = client.get(self.pre_fix + "/notifications", headers=commenter1_headers)
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 验证通知内容
        notifications = r.json.get("data")
        assert len(notifications) > 0
        assert notifications[0].get("type") == "回复"
        assert notifications[0].get("triggerUsername") == "commenter31"

    def test_mark_notification_as_read(self, client, auth):
        """测试标记通知为已读"""
        # 注册第一个用户并发布文章
        auth.register(username="author4", password="password")
        auth.login(username="author4", password="password")
        author_headers = auth.get_headers()

        # 发布文章
        r = client.post(
            self.pre_fix + "/posts",
            headers=author_headers,
            json={"body": "测试文章内容", "bodyHtml": "测试文章内容", "images": []},
        )
        assert r.json.get("code") == 200
        post_id = r.json.get("data")[0].get("id")

        # 注册第二个用户
        auth.register(username="commenter4", password="password")
        auth.login(username="commenter4", password="password")

        # 第二个用户评论第一个用户的文章
        r = client.post(
            self.pre_fix + f"/posts/{post_id}/comments",
            headers=auth.get_headers(),
            json={"body": "这是一条测试评论", "directParentId": None, "at": []},
        )
        assert r.status_code == 200

        # 第一个用户查看通知
        r = client.get(self.pre_fix + "/notifications", headers=author_headers)
        assert r.status_code == 200
        notification_id = r.json.get("data")[-1].get("id")

        # 标记通知为已读
        r = client.patch(
            self.pre_fix + "/notifications",
            headers=author_headers,
            json={"ids": [notification_id]},
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 再次查看通知，确认已标记为已读
        r = client.get(self.pre_fix + "/notifications", headers=author_headers)
        assert r.status_code == 200
        assert r.json.get("data")[-1].get("isRead") is True
