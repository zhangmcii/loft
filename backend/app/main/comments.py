from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request
from . import main
from ..models import Post, Comment, Notification, NotificationType
from ..decorators import permission_required, admin_required
from .. import db
from flask import jsonify, current_app, request
from ..utils.time_util import DateUtils
from ..models import Permission
from .. import socketio
from .. import limiter
from werkzeug.exceptions import TooManyRequests
from ..utils.text_filter import DFAFilter
from ..utils.common import get_avatars_url
from ..utils.response import success, error, not_found
from .. import logger

# 日志
log = logger.get_logger()


# --------------------------- 评论 ---------------------------
@main.route("/post/<int:id>", methods=["POST"])
@limiter.limit("1/second;3/minute", exempt_when=lambda: current_user.role_id == 3)
@jwt_required()
def post(id):
    """发布评论（适配direct_parent关系）"""
    log.info(f"发布评论: post_id={id}")
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
            direct_parent = Comment.query.get(direct_parent_id)
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
        db.session.flush()
        # 通知
        notifications = notice_by_comment_type(
            direct_parent, root_comment, post, comment, at
        )
        db.session.add_all(notifications)
        db.session.commit()
        # 实时推送
        for notification in notifications:
            socketio.emit(
                "new_notification",
                notification.to_json(),
                to=str(notification.receiver_id),
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
        log.error(f"发布评论失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"发布评论失败: {str(e)}")


def notice_by_comment_type(direct_parent, root_comment, post, comment, at_list):
    """
    根评论: 通知文章作者
    一级回复或其他回复: 不通知文章作者，仅通知被直接回复的用户
    """
    notifications = []
    # 根评论
    if not direct_parent and not root_comment:
        if current_user.id != post.author_id:
            notifications.append(
                Notification(
                    receiver_id=post.author_id,
                    trigger_user_id=current_user.id,
                    post_id=post.id,
                    comment_id=comment.id,
                    type=NotificationType.COMMENT,
                )
            )
    # 一级回复或其他回复
    else:
        if current_user.id != direct_parent.author_id:
            notifications.append(
                Notification(
                    receiver_id=direct_parent.author_id,
                    trigger_user_id=current_user.id,
                    post_id=post.id,
                    comment_id=comment.id,
                    type=NotificationType.REPLY,
                )
            )

    # @的通知
    for receiver_id in at_list:
        notifications.append(
            Notification(
                receiver_id=receiver_id,
                trigger_user_id=current_user.id,
                post_id=post.id,
                comment_id=comment.id,
                type=NotificationType.AT,
            )
        )
    return notifications


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
    log.info("管理评论")
    page = request.args.get("page", 1, type=int)
    comments, total = all_comments(page)
    return success(data=comments, total=total)


@main.route("/moderate/enable/<int:id>")
@jwt_required()
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    """恢复评论"""
    log.info(f"恢复评论: id={id}")
    try:
        comment = Comment.query.get_or_404(id)
        comment.disabled = False
        db.session.add(comment)
        db.session.commit()
        comments, total = all_comments(1)
        return success(message="评论已恢复", data=comments, total=total)
    except Exception as e:
        log.error(f"恢复评论失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"恢复评论失败: {str(e)}")


@main.route("/moderate/disable/<int:id>")
@jwt_required()
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    """禁用评论"""
    log.info(f"禁用评论: id={id}")
    try:
        comment = Comment.query.get_or_404(id)
        comment.disabled = True
        db.session.add(comment)
        db.session.commit()
        comments, total = all_comments(1)
        return success(message="评论已禁用", data=comments, total=total)
    except Exception as e:
        log.error(f"禁用评论失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"禁用评论失败: {str(e)}")