# 日志
import logging

from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required, verify_jwt_in_request
from werkzeug.exceptions import TooManyRequests

from .. import db, limiter
from ..decorators import permission_required
from ..models import Comment, NotificationType, Permission, Post
from ..mycelery.notification_task import create_comment_notifications
from ..utils.common import get_avatars_url
from ..utils.response import error, success
from ..utils.text_filter import DFAFilter
from ..utils.time_util import DateUtils
from . import main


# --------------------------- 评论 ---------------------------
@main.route("/post/<int:id>", methods=["POST"])
@limiter.limit("1/second;3/minute", exempt_when=lambda: current_user.role_id == 3)
@jwt_required()
def post(id):
    """发布评论（适配direct_parent关系）"""
    logging.info(f"发布评论: post_id={id}")
    post = Post.query.get_or_404(id)
    verify_jwt_in_request()
    data = request.get_json()
    at = data.get("at")
    # 直接父id
    direct_parent_id = data.get("directParentId")
    try:
        direct_parent = None
        root_comment = None

        # 若是根评论，  则direct_parent=root_commentNone = None
        # 若是一级回复，则direct_parent=root_commentNone = 根评论对象
        # 若是其他回复，则direct_parent = 直接评论对象， root_commentNone = 根评论对象
        if direct_parent_id:
            # 直接父id
            direct_parent = db.session.get(Comment, direct_parent_id)
            # 获取根评论：如果父评论本身有根评论则继承，否则父评论就是根评论
            root_comment = (
                direct_parent.root_comment
                if direct_parent.root_comment_id
                else direct_parent
            )
        # 创建评论（设置两个父级关系）
        comment = Comment(
            body=DFAFilter().filter(data.get("body"), "*"),
            post=post,
            author=current_user,
            direct_parent=direct_parent,
            root_comment=root_comment,
        )
        db.session.add(comment)
        db.session.commit()
        # 异步通知
        create_comment_notification(
            post.id, comment.id, direct_parent, root_comment, post, at
        )
        current_comment = {
            "id": comment.id,
            "parentId": comment.root_comment_id,
            "uid": current_user.id,
            "content": comment.body,
            "createTime": DateUtils.datetime_to_str(comment.timestamp),
            "user": {
                "username": (
                    current_user.nickname
                    if current_user.nickname
                    else current_user.username
                ),
                "avatar": get_avatars_url(current_user.image),
            },
            "reply": "",
        }
        return success(data=current_comment)
    except TooManyRequests:
        raise
    except Exception as e:
        logging.error(f"发布评论失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"发布评论失败: {str(e)}")


def create_comment_notification(
    post_id, comment_id, direct_parent, root_comment, post, at_list
):
    """异步创建评论通知"""
    notifications_data = []

    # 根评论：通知文章作者
    if not direct_parent and not root_comment:
        if current_user.id != post.author_id:
            notifications_data.append((post.author_id, NotificationType.COMMENT))
    # 回复：通知被直接回复的用户
    elif direct_parent:
        if current_user.id != direct_parent.author_id:
            notifications_data.append((direct_parent.author_id, NotificationType.REPLY))

    # @通知
    if at_list:
        notifications_data.extend(
            [(receiver_id, NotificationType.AT) for receiver_id in at_list]
        )

    create_comment_notifications.delay(
        post_id, comment_id, current_user.id, notifications_data
    )


def all_comments(page):
    query = Comment.query
    pagination = query.order_by(Comment.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config["FLASKY_COMMENTS_PER_PAGE"],
        error_out=False,
    )
    comments = [
        {
            "body": item.body,
            "timestamp": DateUtils.datetime_to_str(item.timestamp),
            "author": item.author.username,
            "image": get_avatars_url(item.author.image),
            "id": item.id,
            "disabled": item.disabled,
        }
        for item in pagination.items
    ]
    total = query.count()
    return comments, total


@main.route("/moderate")
@jwt_required()
@permission_required(Permission.MODERATE)
def moderate():
    """管理评论"""
    logging.info("管理评论")
    page = request.args.get("page", 1, type=int)
    comments, total = all_comments(page)
    return success(data=comments, total=total)


@main.route("/moderate/enable/<int:id>")
@jwt_required()
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    """恢复评论"""
    logging.info(f"恢复评论: id={id}")
    try:
        comment = Comment.query.get_or_404(id)
        comment.disabled = False
        db.session.commit()
        comments, total = all_comments(1)
        return success(message="评论已恢复", data=comments, total=total)
    except Exception as e:
        logging.error(f"恢复评论失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"恢复评论失败: {str(e)}")


@main.route("/moderate/disable/<int:id>")
@jwt_required()
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    """禁用评论"""
    logging.info(f"禁用评论: id={id}")
    try:
        comment = Comment.query.get_or_404(id)
        comment.disabled = True
        db.session.commit()
        comments, total = all_comments(1)
        return success(message="评论已禁用", data=comments, total=total)
    except Exception as e:
        logging.error(f"禁用评论失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"禁用评论失败: {str(e)}")
