import pytest
from base64 import b64encode
from app import db
from flask import url_for
from app.models import User, Role, Post, Comment


@pytest.mark.usefixtures('flask_pre_and_post_process')
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

    def test_posts(self, client, auth):
        r = Role.query.filter_by(name='User').first()
        assert r
        auth.register()
        auth.login()
        # 发布文章
        client.post('/api/v1/posts/', headers= auth.get_headers(), json={'body': '666'})

        # # 获取刚刚发布的文章
        # r = client.get('/api/v1/posts/',headers= auth.get_headers())
        # assert r.status_code == 200
        # assert r.json.get('posts')[0].get('body') == '666'
        # assert r.json.get('posts')[0].get('author') == 'test'

