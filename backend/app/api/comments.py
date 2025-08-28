from .decorators import DecoratedMethodView
from flask_jwt_extended import jwt_required, current_user

from . import api
from ..models import Post, Comment, Notification, NotificationType, Permission
from ..decorators import permission_required
from .. import db
from flask import current_app, request
from ..utils.time_util import DateUtils
from ..utils.socket_helper import send_notification
from .. import limiter
from werkzeug.exceptions import TooManyRequests
from ..utils.text_filter import DFAFilter
from ..utils.common import get_avatars_url
from ..utils.response import success, error
from .. import logger

# 日志
log = logger.get_logger()


# --------------------------- 评论 ---------------------------


@api.route("/comments")
@jwt_required()
@permission_required(Permission.MODERATE)
def moderate():
    """管理评论"""
    log.info("管理评论")
    page = request.args.get("page", 1, type=int)
    comments, total = CommentManageApi.all_comments(page)
    return success(data=comments, total=total)


@api.route('/comments/<int:comment_id>/replies')
def get_comment_replies(comment_id):
    log.info("获取评论回复")
    root_comment_id = comment_id
    page = request.args.get('page', 1, type=int)
    # 分页时不自动嵌套，前端按需请求
    replies, total = CommentApi.get_replies_by_parent(root_comment_id=root_comment_id, page=page)
    return success(
        data=replies,
        extra={
            'total': total,
            'current_page': page
        }
    )


class CommentApi(DecoratedMethodView):
    method_decorators = {
        'get': [],
        'post': [jwt_required(), limiter.limit(
            "1/second;3/minute",
            exempt_when=lambda: current_user.role_id == 3
        )]
    }

    @staticmethod
    def get_replies_by_parent(root_comment_id, page):
        """
        获取指定父评论的所有直接回复
        :param root_comment_id: 根父评论ID
        """
        # 基础查询：直接回复
        query = Comment.query.filter_by(root_comment_id=root_comment_id).order_by(Comment.timestamp.desc())
        # 分页查询
        pagination = query.paginate(page=page, per_page=current_app.config['FLASKY_COMMENTS_REPLY_PER_PAGE'],
                                    error_out=False)
        replies = []
        for reply in pagination.items:
            reply_data = reply.to_json_new()
            replies.append(reply_data)

        return replies, query.count()

    @staticmethod
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

    def get(self, post_id):
        log.info(f"获取文章评论: post_id={post_id}")
        post = Post.query.get_or_404(post_id)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('size', current_app.config['FLASKY_COMMENTS_PER_PAGE'], type=int)
        # 获取根评论分页（parent_comment_id为None）
        root_comments_pagination = post.comments.filter(Comment.root_comment_id.is_(None)).order_by(
            Comment.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

        comments = []
        for root_comment in root_comments_pagination.items:
            comment_data = root_comment.to_json_new()
            # 获取该根评论下的第一层直接回复（direct_parent_id=根评论ID）
            first_level_replies, reply_total = CommentApi.get_replies_by_parent(root_comment.id, page=1)
            comment_data.update({
                'reply': {
                    'list': first_level_replies,
                    'total': reply_total,
                }
            })
            comments.append(comment_data)

        return success(
            data=comments,
            extra={
                'total': root_comments_pagination.total,
                'current_page': page
            }
        )

    def post(self, post_id):
        """发布评论（适配direct_parent关系）"""
        log.info(f"发布评论: post_id={post_id}")
        post = Post.query.get_or_404(post_id)
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
            notifications = CommentApi.notice_by_comment_type(
                direct_parent, root_comment, post, comment, at
            )
            db.session.add_all(notifications)
            db.session.commit()
            # 实时推送
            for notification in notifications:
                send_notification(notification.receiver_id, notification.to_json())
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


class CommentManageApi(DecoratedMethodView):
    """评论管理"""
    method_decorators = {
        'share': [jwt_required(), permission_required(Permission.MODERATE)],

        'post': [jwt_required(), limiter.limit(
            "1/second;3/minute",
            exempt_when=lambda: current_user.role_id == 3
        )]
    }

    @staticmethod
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

    def patch(self, comment_id):
        """禁用/恢复评论"""
        log.info(f"恢复评论: id={comment_id}")
        status = request.json.get('status')
        try:
            comment = Comment.query.get_or_404(comment_id)
            if status == 'enable':
                comment.disabled = False
            elif status == 'disable':
                comment.disabled = True
            else:
                return error(400, f"传递参数错误, status{status}")
            db.session.add(comment)
            db.session.commit()
            comments, total = CommentManageApi.all_comments(1)
            return success(message="操作成功", data=comments, total=total)
        except Exception as e:
            log.error(f"{status}操作失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"{status}操作失败: {str(e)}")

    def delete(self, comment_id):
        """删除评论"""
        return error(500, f"操作失败")

    def put(self, comment_id):
        """修改评论"""
        return error(500, f"操作失败: ")


def register_comment_api(bp, *, comment_url, comment_manage_url):
    comment = CommentApi.as_view('comments')
    comment_manage = CommentManageApi.as_view('comments_manage')
    bp.add_url_rule(comment_url, view_func=comment)
    bp.add_url_rule(comment_manage_url, view_func=comment_manage)
