import os
import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models import User, Role, Post, Comment, Follow, Permission, Tag

@pytest.fixture(scope='module')
def app():
    """创建并配置一个Flask应用实例用于测试"""
    app = create_app('testing')
    
    # 创建应用上下文
    with app.app_context():
        db.create_all()
        Role.insert_roles()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture(scope='module')
def runner(app):
    """创建测试命令运行器"""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def test_user(app):
    """创建测试用户"""
    with app.app_context():
        # 使用User模型的password属性setter方法设置密码
        user = User(
            email='test@example.com',
            username='testuser',
            confirmed=True
        )
        user.password = 'password'  # 这会调用password.setter方法，正确设置password_hash
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        # 清理
        db.session.delete(user)
        db.session.commit()

@pytest.fixture(scope='function')
def admin_user(app):
    """创建管理员用户"""
    with app.app_context():
        admin = User(
            email='admin@example.com',
            username='admin',
            confirmed=True
        )
        admin.password = 'password'  # 这会调用password.setter方法，正确设置password_hash
        admin_role = Role.query.filter_by(name='Administrator').first()
        admin.role = admin_role
        db.session.add(admin)
        db.session.commit()
        
        yield admin
        
        # 清理
        db.session.delete(admin)
        db.session.commit()

@pytest.fixture(scope='function')
def test_token(app, test_user):
    """为测试用户创建JWT令牌"""
    with app.app_context():
        token = create_access_token(identity=test_user)
        return token

@pytest.fixture(scope='function')
def admin_token(app, admin_user):
    """为管理员用户创建JWT令牌"""
    with app.app_context():
        token = create_access_token(identity=admin_user)
        return token

@pytest.fixture(scope='function')
def test_post(app, test_user):
    """创建测试文章"""
    with app.app_context():
        post = Post(
            body='测试文章内容',
            author=test_user
        )
        db.session.add(post)
        db.session.commit()
        
        yield post
        
        # 清理
        db.session.delete(post)
        db.session.commit()

@pytest.fixture(scope='function')
def test_comment(app, test_user, test_post):
    """创建测试评论"""
    with app.app_context():
        comment = Comment(
            body='测试评论内容',
            author=test_user,
            post=test_post
        )
        db.session.add(comment)
        db.session.commit()
        
        yield comment
        
        # 清理
        db.session.delete(comment)
        db.session.commit()

@pytest.fixture(scope='function')
def test_follow(app, test_user, admin_user):
    """创建测试关注关系"""
    with app.app_context():
        test_user.follow(admin_user)
        db.session.commit()
        
        yield
        
        # 清理
        test_user.unfollow(admin_user)
        db.session.commit()

@pytest.fixture(scope='function')
def test_tag(app):
    """创建测试标签"""
    with app.app_context():
        tag = Tag(name='测试标签')
        db.session.add(tag)
        db.session.commit()
        
        yield tag
        
        # 清理
        db.session.delete(tag)
        db.session.commit()