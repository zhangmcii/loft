import pytest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission, Follow
from app.utils.time_util import DateUtils


@pytest.mark.usefixtures('flask_pre_and_post_process')
class TestUserModel:
    
    def test_password_setter(self):
        u = User(password='cat')
        assert u.password_hash is not None
        
    def test_no_password_getter(self):
        u = User(password='cat')
        with pytest.raises(AttributeError):
            u.password
            
    def test_password_verification(self):
        u = User(password='cat')
        assert u.verify_password('cat') == True
        assert u.verify_password('dog') == False
        
    def test_password_salts_are_random(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        assert u1.password_hash != u2.password_hash
        
    def test_user_role(self):
        u = User(username='jack', password='cat')
        assert u.can(Permission.FOLLOW)
        assert u.can(Permission.COMMENT)
        assert u.can(Permission.WRITE)
        assert not u.can(Permission.MODERATE)
        assert not u.can(Permission.ADMIN)


    def test_moderator_role(self):
        r = Role.query.filter_by(name='Moderator').first()
        u = User(email='john@example.com', password='cat', role=r)
        assert u.can(Permission.FOLLOW)
        assert u.can(Permission.COMMENT)
        assert u.can(Permission.WRITE)
        assert u.can(Permission.MODERATE)
        assert not u.can(Permission.ADMIN)

    def test_administrator_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='john@example.com', password='cat', role=r)
        assert u.can(Permission.FOLLOW)
        assert u.can(Permission.COMMENT)
        assert u.can(Permission.WRITE)
        assert u.can(Permission.MODERATE)
        assert u.can(Permission.ADMIN)
        
    def test_timestamp(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        assert (datetime.now() - u.member_since).total_seconds() < 3
        assert (datetime.now() - u.last_seen).total_seconds() < 3
        
    def test_ping(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        assert u.last_seen > last_seen_before
    
    def test_follow(self):
        u1 = User(username='jack',password='cat')
        u2 = User(username='smith',password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        assert not u1.is_following(u2)
        assert not u2.is_followed_by(u1)
        timestamp_before = datetime.now()
        time.sleep(1)
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.now()
        assert u1.is_following(u1)
        assert u1.is_following(u2)
        assert u2.is_followed_by(u1)
        assert u1.followed.count() == 2
        assert u2.followers.count() == 2
        f = u1.followed.all()[-1]
        assert f.followed == u2
        assert timestamp_before <= f.timestamp <= timestamp_after
        
        # 此处 f = u2.followers.all()[-1] 为 u2自己 
        f = u2.followers.all()[0]
        assert f.follower == u1
        
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        assert u1.is_following(u1)
        assert not u1.is_following(u2)
        assert not u2.is_followed_by(u1)
        assert u1.followed.count() == 1
        assert u2.followers.count() == 1
        assert Follow.query.count() == 2
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        assert Follow.query.count() == 1
        
    def test_to_json(self,app):
        import warnings
        warnings.warn(UserWarning('请使用新版本的API。'))
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        with app.test_request_context('/'):
            json_user = u.to_json(u)
        expected_keys = ['url', 'username', 'member_since', 'last_seen',
                         'posts_url', 'followed_posts_url', 'post_count']
        assert sorted(json_user.keys()), sorted(expected_keys)
        assert '/api/v1/users/' + str(u.id) == json_user['url']
       
        
