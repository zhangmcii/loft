# 日志
import logging

from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required

from .. import db
from ..api.users import get_user_data
from ..decorators import permission_required
from ..models import Follow, Permission, User
from ..utils.common import get_avatars_url
from ..utils.response import error, not_found, success
from ..utils.time_util import DateUtils
from . import main


# --------------------------- 关注 ---------------------------
@main.route("/follow/<username>")
@jwt_required()
@permission_required(Permission.FOLLOW)
def follow(username):
    """关注用户"""
    logging.info(f"关注用户: {current_user.username} -> {username}")
    user = User.query.filter_by(username=username).first()
    if user is None:
        return not_found("用户名不存在")
    if current_user.is_following(user):
        return error(400, "你已经关注了该用户")

    try:
        current_user.follow(user)
        db.session.commit()
        data = get_user_data(username)
        return success(data=data)
    except Exception as e:
        logging.error(f"关注用户失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"关注用户失败: {str(e)}")


@main.route("/unfollow/<username>")
@jwt_required()
@permission_required(Permission.FOLLOW)
def unfollow(username):
    """取消关注用户"""
    logging.info(f"取消关注用户: {current_user.username} -> {username}")
    user = User.query.filter_by(username=username).first()
    if user is None:
        return not_found("用户名不存在")
    if not current_user.is_following(user):
        return error(400, "你未关注该用户")

    try:
        current_user.unfollow(user)
        db.session.commit()
        data = get_user_data(username)
        return success(data=data)
    except Exception as e:
        logging.error(f"取消关注用户失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"取消关注用户失败: {str(e)}")


@main.route("/followers/<username>")
def followers(username):
    """获取用户的粉丝列表"""
    logging.info(f"获取用户粉丝列表: username={username}")
    user = User.query.filter_by(username=username).first()
    if user is None:
        return not_found("用户名不存在")

    page = request.args.get("page", 1, type=int)
    pagination = user.followers.order_by(Follow.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["FLASKY_FOLLOWERS_PER_PAGE"],
        error_out=False,
    )
    follows = []
    for item in pagination.items:
        if item.follower.username != username:
            is_following_back = (
                Follow.query.filter_by(follower=user, followed=item.follower).first()
                is not None
            )
            follows.append(
                {
                    "id": item.follower.id,
                    "nickname": item.follower.nickname,
                    "username": item.follower.username,
                    "image": get_avatars_url(item.follower.image),
                    "timestamp": DateUtils.datetime_to_str(item.timestamp),
                    "is_following": is_following_back,
                }
            )
    return success(data=follows, total=user.followers.count() - 1)


@main.route("/followed_by/<username>")
def followed_by(username):
    """获取用户关注的人列表"""
    logging.info(f"获取用户关注列表: username={username}")
    user = User.query.filter_by(username=username).first()
    if user is None:
        return not_found("用户名不存在")

    page = request.args.get("page", 1, type=int)
    pagination = user.followed.order_by(Follow.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["FLASKY_FOLLOWERS_PER_PAGE"],
        error_out=False,
    )
    follows = []
    for item in pagination.items:
        if item.followed.username != username:
            is_following_back = (
                Follow.query.filter_by(follower=item.followed, followed=user).first()
                is not None
            )
            follows.append(
                {
                    "id": item.followed.id,
                    "nickname": item.followed.nickname,
                    "username": item.followed.username,
                    "image": get_avatars_url(item.followed.image),
                    "timestamp": DateUtils.datetime_to_str(item.timestamp),
                    "is_following_back": is_following_back,
                }
            )
    return success(data=follows, total=user.followed.count() - 1)
