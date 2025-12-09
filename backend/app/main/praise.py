# 日志
import logging

from flask import request
from flask_jwt_extended import current_user, jwt_required, verify_jwt_in_request

from .. import db
from ..models import Comment, Post, Praise
from ..mycelery.notification_task import create_like_notifications
from ..utils.response import error, success
from . import main


# --------------------------- 点赞功能 ---------------------------
@main.route("/praise/<int:id>", methods=["GET", "POST"])
@jwt_required()
def praise(id):
    """文章点赞"""
    logging.info(f"文章点赞: id={id}")
    post = Post.query.get_or_404(id)
    if request.method == "POST":
        # POST 请求需要 JWT 验证
        verify_jwt_in_request()
        # 防止用户重复点赞
        p = Praise.query.filter_by(author_id=current_user.id, post_id=id).first()
        if p:
            return error(400, "您已经点赞过了~")

        try:
            praise = Praise(post=post, author=current_user)
            db.session.add(praise)
            db.session.commit()

            # 异步创建点赞通知
            if current_user.id != post.author_id:
                create_like_notifications.delay(
                    post.id, None, current_user.id, post.author_id
                )

            return success(
                data={"praise_total": post.praise.count(), "has_praised": True}
            )
        except Exception as e:
            logging.error(f"文章点赞失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"操作失败，已回滚: {str(e)}")

    return success(data={"praise_total": post.praise.count()})


@main.route("/praise/comment/<int:id>", methods=["GET", "POST"])
@jwt_required()
def praise_comment(id):
    """评论点赞"""
    logging.info(f"评论点赞: id={id}")
    comment = Comment.query.get_or_404(id)
    if request.method == "POST":
        # POST 请求需要 JWT 验证
        verify_jwt_in_request()

        try:
            praise = Praise(comment=comment, author=current_user)
            db.session.add(praise)
            db.session.commit()

            # 异步创建点赞通知
            if current_user.id != comment.author_id:
                create_like_notifications.delay(
                    comment.post_id, comment.id, current_user.id, comment.author_id
                )

            return success(data={"praise_total": comment.praise.count()})
        except Exception as e:
            logging.error(f"评论点赞失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"点赞操作失败，已回滚: {str(e)}")

    return success(data={"praise_total": comment.praise.count()})


@main.route("/has_praised/<int:post_id>")
def has_praised_comment_id(post_id):
    """查找某文章下当前用户已点赞的评论id"""
    logging.info(f"查询用户已点赞评论: post_id={post_id}")
    comment_ids = (
        db.session.query(Praise.comment_id)
        .join(Comment)
        .filter(
            Praise.author_id == current_user.id,
            Comment.post_id == post_id,
            Praise.comment_id.isnot(None),
        )
        .distinct()
        .all()
    )
    return success(data=[item[0] for item in comment_ids])
