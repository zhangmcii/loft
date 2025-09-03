from base64 import b64encode


class TestPraiseCommentCase:
    """测试点赞和评论功能"""

    def get_api_headers(self, username, password):
        return {
            "Authorization": "Basic "
            + b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
            "Accept": "application/json",
            "Content-type": "application/json",
        }

    def test_post_comment_and_praise(self, client, auth):
        """测试发表评论和点赞文章"""
        # 注册并登录用户
        auth.register()
        auth.login()

        # 发布一篇文章
        r = client.post(
            "/",
            headers=auth.get_headers(),
            json={"body": "测试文章内容", "bodyHtml": "测试文章内容", "images": []},
        )
        assert r.json.get("code") == 200
        post_id = r.json.get("data")[0].get("id")

        # 发表评论
        r = client.post(
            f"/post/{post_id}",
            headers=auth.get_headers(),
            json={"body": "这是一条测试评论", "directParentId": None, "at": []},
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200
        assert "这是一条" in r.json.get("data").get("content")

        # 获取文章的评论列表
        r = client.get(f"/api/v1/posts/{post_id}/comments/", headers=auth.get_headers())
        assert r.status_code == 200
        assert r.json.get("code") == 200
        assert len(r.json.get("data")) > 0

        # 点赞文章
        r = client.post(f"/praise/{post_id}", headers=auth.get_headers())
        assert r.status_code == 200
        assert r.json.get("code") == 200
        assert r.json.get("data").get("praise_total") == 1
        assert r.json.get("data").get("has_praised") is True

        # 重复点赞应该失败
        r = client.post(f"/praise/{post_id}", headers=auth.get_headers())
        assert r.status_code == 200
        assert r.json.get("code") == 400  # 应该返回错误码
        assert "已经点赞过了" in r.json.get("message")

    def test_comment_reply_and_praise(self, client, auth):
        """测试评论回复和点赞评论"""
        # 注册并登录用户
        auth.register()
        auth.login()

        # 发布一篇文章
        r = client.post(
            "/",
            headers=auth.get_headers(),
            json={"body": "测试文章内容", "bodyHtml": "测试文章内容", "images": []},
        )
        assert r.json.get("code") == 200
        post_id = r.json.get("data")[-1].get("id")

        # 发表根评论
        r = client.post(
            f"/post/{post_id}",
            headers=auth.get_headers(),
            json={"body": "这是一条根评论", "directParentId": None, "at": []},
        )
        assert r.status_code == 200
        comment_id = r.json.get("data").get("id")

        # 回复评论
        r = client.post(
            f"/post/{post_id}",
            headers=auth.get_headers(),
            json={"body": "这是对根评论的回复", "directParentId": comment_id, "at": []},
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200

        # 获取评论的回复
        r = client.get(
            f"/api/v1/reply_comments/?rootCommentId={comment_id}",
            headers=auth.get_headers(),
        )
        assert r.status_code == 200
        assert r.json.get("code") == 200
        assert len(r.json.get("data")) > 0
        assert "这是对根评论" in r.json.get("data")[0].get("content")

        # 点赞评论
        r = client.post(f"/praise/comment/{comment_id}", headers=auth.get_headers())
        assert r.status_code == 200
        assert r.json.get("code") == 200
        assert r.json.get("data").get("praise_total") == 1

        # 检查已点赞的评论ID
        r = client.get(f"/has_praised/{post_id}", headers=auth.get_headers())
        assert r.status_code == 200
        assert r.json.get("code") == 200
        assert comment_id in r.json.get("data")
