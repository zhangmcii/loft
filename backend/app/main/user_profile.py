# 日志
import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy import and_

from .. import db
from ..decorators import admin_required
from ..models import Image, ImageType, Role, User
from ..utils.common import get_avatars_url
from ..utils.response import error, success
from . import main


# --------------------------- 编辑资料 ---------------------------
@main.route("/edit-profile", methods=["POST"])
@jwt_required()
def edit_profile():
    """编辑用户资料"""

    logging.info(f"编辑用户资料: user_id={current_user.id}")
    try:
        user_info = request.get_json()
        current_user.nickname = user_info.get("nickname")
        current_user.location = user_info.get("location")
        current_user.about_me = user_info.get("about_me")
        db.session.commit()
        return success(message="用户资料更新成功")
    except Exception as e:
        logging.error(f"编辑用户资料失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"编辑用户资料失败: {str(e)}")


@main.route("/edit-profile/<int:id>", methods=["POST"])
@jwt_required()
@admin_required
def edit_profile_admin(id):
    """管理员编辑用户资料"""
    logging.info(f"管理员编辑用户资料: user_id={id}")
    try:
        user = User.query.get_or_404(id)
        user_info = request.get_json()
        user.email = user_info.get("email")
        user.username = user_info.get("username")
        user.confirmed = user_info.get("confirmed")
        user.role = Role.query.get(int(user_info.get("role")))

        user.nickname = user_info.get("nickname")
        user.location = user_info.get("location")
        user.about_me = user_info.get("about_me")

        db.session.commit()
        return success(message="用户资料更新成功")
    except Exception as e:
        logging.error(f"管理员编辑用户资料失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"编辑用户资料失败: {str(e)}")


@main.route("/image", methods=["POST"])
@jwt_required()
def add_user_image():
    """存储用户图像地址"""
    logging.info(f"存储用户图像地址: user_id={current_user.id}")
    try:
        image = request.get_json().get("image")
        current_user.image = image
        db.session.commit()
        return success(data={"image": get_avatars_url(image)})
    except Exception as e:
        logging.error(f"存储用户图像地址失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"存储用户图像地址失败: {str(e)}")


@main.route("/can/<int:perm>")
@jwt_required(optional=True)
def can(perm):
    """检查用户权限"""
    logging.info(f"检查用户权限: perm={perm}")
    if current_user:
        return success(data=current_user.can(perm))
    return success(data=False)


@main.route("/user_posts")
@admin_required
@jwt_required()
def generate_user_posts():
    """批量生成用户和文章"""
    logging.info("批量生成用户和文章")
    try:
        from ..fake import Fake
        from ..models import Role

        Role.insert_roles()
        Fake.users()
        Fake.posts()
        return success(message="用户和文章生成成功")
    except Exception as e:
        logging.error(f"生成用户和文章失败: {str(e)}", exc_info=True)
        return error(500, f"生成用户和文章失败: {str(e)}")


@main.route("/socketData")
@admin_required
@jwt_required()
def online():
    """获取在线用户信息"""
    logging.info("获取在线用户信息")
    from ..models import User
    from ..utils.socket_util import ManageSocket

    manage_socket = ManageSocket()
    # 在线人数信息
    user_ids = manage_socket.user_socket.keys()
    users = []
    for user_id in user_ids:
        u = User.query.get(user_id)
        users.append({"username": u.username, "nickName": u.nickname})
    online_total = len(users)
    return success(data=users, total=online_total)


@main.route("/user/<int:user_id>/interest_images")
def get_favorite_book_image(user_id):
    """获取用户兴趣图片"""
    logging.info(f"获取用户兴趣图片: user_id={user_id}")
    book_images = Image.query.filter(
        and_(Image.type == ImageType.BOOK, Image.related_id == user_id)
    ).all()
    return success(data=[image.to_json() for image in book_images])
