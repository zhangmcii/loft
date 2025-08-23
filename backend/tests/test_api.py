from base64 import b64encode
from app.models import User, Role, Post, Comment


class TestApiCase:

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode((username + ":" + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }

    def test_no_auth(self, client):
        r = client.get('/api/v1/posts/', content_type='application/json')
        assert r.status_code == 200
        assert r.json.get('code') == 200

    def test_posts(self, client, auth):
        """模拟新用户注册、登陆，发布普通文章，图文，markdown文章的过程"""
        r = Role.query.filter_by(name='User').first()
        assert r
        auth.register()
        auth.login()

        # 发布普通文章
        r = client.post('/', headers= auth.get_headers(), json={'body': '666', 'bodyHtml':'666', 'images': []})
        assert r.json.get('code') == 200

        # 获取刚刚发布的文章
        r = client.get('/', headers= auth.get_headers())
        assert r.status_code == 200
        assert r.json.get('data')[0].get('body') == '666'
        assert r.json.get('data')[0].get('author') == 'test'

        # 发布图文文章(要连接redis)
        r = client.post('/rich_post', headers=auth.get_headers(), json={'content': '测试图文文章', 'imageUrls': ['123.png', '456.png']})
        response = r.json
        assert response.get('code') == 200
        new_post = response.get('data')[0]
        assert '测试图文文章' in new_post.get('body')
        assert len(new_post.get('post_images')) == 2


        # 发布markdown文章
        r = client.post('/', headers=auth.get_headers(), json={'body': '测试markdown文章[图片](1)', 'bodyHtml': '测试markdown文章<img src="1" alt="图片">', 'images': [{'url':'abc.png', 'pos':1},{'url':'efg.png', 'pos':2}]})
        assert r.json.get('code') == 200
        assert r.json.get('total') == 3
        data = r.json.get('data')
        assert '测试markdown文章' in data[2].get('body')
        assert 'abc.png' in data[2].get('body_html')
        assert 'abc.png' in data[2].get('body_html')
        assert '1' in data[2].get('pos')








