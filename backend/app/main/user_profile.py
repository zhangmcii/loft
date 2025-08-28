from flask_jwt_extended import jwt_required, current_user
from . import main
from ..models import User, Role, Image, ImageType
from ..decorators import admin_required
from .. import db
from flask import jsonify, request
from ..utils.common import get_avatars_url
from ..utils.response import success, error, not_found
from .. import logger
from sqlalchemy import and_

# 日志
log = logger.get_logger()


# --------------------------- 编辑资料 ---------------------------
@main.route("/edit-profile", methods=["POST"])
@jwt_required()
def edit_profile():
    """编辑用户资料"""

    log.info(f"编辑用户资料: user_id={current_user.id}")
    try:
        user_info = request.get_json()
        current_user.nickname = user_info.get("nickname")
        current_user.location = user_info.get("location")
        current_user.about_me = user_info.get("about_me")
        db.session.add(current_user)
        db.session.commit()
        return success(message="用户资料更新成功")
    except Exception as e:
        log.error(f"编辑用户资料失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"编辑用户资料失败: {str(e)}")


@main.route("/edit-profile/<int:id>", methods=["POST"])
@jwt_required()
@admin_required
def edit_profile_admin(id):
    """管理员编辑用户资料"""
    log.info(f"管理员编辑用户资料: user_id={id}")
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

        db.session.add(user)
        db.session.commit()
        return success(message="用户资料更新成功")
    except Exception as e:
        log.error(f"管理员编辑用户资料失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"编辑用户资料失败: {str(e)}")


@main.route("/image", methods=["POST"])
@jwt_required()
def add_user_image():
    """存储用户图像地址"""
    log.info(f"存储用户图像地址: user_id={current_user.id}")
    try:
        image = request.get_json().get("image")
        current_user.image = image
        db.session.add(current_user)
        db.session.commit()
        return success(data={"image": get_avatars_url(image)})
    except Exception as e:
        log.error(f"存储用户图像地址失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"存储用户图像地址失败: {str(e)}")


# @main.route("/users/<username>")
# @jwt_required(optional=True)
# def get_user_by_username(username):
#     """ 根据用户名获取用户数据
#         前端已不再使用
#     """
#     log.info(f"获取用户信息: username={username}")
#     user = User.query.filter_by(username=username).first()
#     data = get_user_data(username)
#     return success(data=data)





@main.route("/can/<int:perm>")
@jwt_required(optional=True)
def can(perm):
    """检查用户权限"""
    log.info(f"检查用户权限: perm={perm}")
    if current_user:
        return success(data=current_user.can(perm))
    return success(data=False)


@main.route("/user_posts")
@admin_required
@jwt_required()
def generate_user_posts():
    """批量生成用户和文章"""
    log.info("批量生成用户和文章")
    try:
        from ..fake import Fake
        from ..models import Role
        Role.insert_roles()
        Fake.users()
        Fake.posts()
        return success(message="用户和文章生成成功")
    except Exception as e:
        log.error(f"生成用户和文章失败: {str(e)}", exc_info=True)
        return error(500, f"生成用户和文章失败: {str(e)}")
    
    
@main.route("/socketData")
@admin_required
@jwt_required()
def online():
    """获取在线用户信息"""
    log.info("获取在线用户信息")
    from ..utils.socket_util import ManageSocket
    from ..models import User
    
    manage_socket = ManageSocket()
    # 在线人数信息
    user_ids = manage_socket.user_socket.keys()
    users = []
    for user_id in user_ids:
        u = User.query.get(user_id)
        users.append({"username": u.username, "nickName": u.nickname})
    online_total = len(users)
    return success(data=users, extra={"total": online_total})


@main.route("/user/<int:user_id>/interest_images")
def get_favorite_book_image(user_id):
    """获取用户兴趣图片"""
    log.info(f"获取用户兴趣图片: user_id={user_id}")
    book_images = Image.query.filter(
        and_(Image.type == ImageType.BOOK, Image.related_id == user_id)
    ).all()
    return success(data=[image.to_json() for image in book_images])
