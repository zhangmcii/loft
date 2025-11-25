import logging
import os

from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from .. import db, limiter, socketio
from ..decorators import DecoratedMethodView
from ..main.uploads import del_qiniu_image
from ..models import (
    Comment,
    Follow,
    Image,
    ImageType,
    Notification,
    NotificationType,
    Permission,
    Post,
    PostType,
    Praise,
    User,
)
from ..utils.response import error, success
from ..utils.time_util import DateUtils
from ..utils.common import get_avatars_url
from .. import cache
from ..decorators import sql_profile


class PostItemApi(DecoratedMethodView):
    method_decorators = {
        "get": [],
        "delete": [jwt_required()],
        "patch": [jwt_required()],
    }

    @staticmethod
    def soft_delete(post):
        logging.info(f"逻辑删除文章: id={post.id}")
        post.deleted = True
        db.session.add(post)
        db.session.commit()

    @staticmethod
    def hard_delete(post):
        # 删除文章，同时也要删除文章中的图片url
        is_contain_image, data = None, None
        try:
            is_contain_image = post.type == PostType.IMAGE
            to_del_urls = []
            if is_contain_image:
                post_images = (
                    Image.query.filter(
                        Image.type == ImageType.POST, Image.related_id == post.id
                    )
                    .order_by(Image.id.asc())
                    .all()
                )
                to_del_urls = [image.url for image in post_images]
                # 删除图片
                data = {
                    "bucket_name": os.getenv("QINIU_BUCKET_NAME", ""),
                    "keys": to_del_urls,
                }
            db.session.delete(post)
            db.session.commit()
        except Exception as e:
            logging.error(f"删除文章失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"删除文章失败: {str(e)}")

        if is_contain_image and to_del_urls:
            # 传递j,执行图片删除
            del_qiniu_image(**data)

    def get(self, id):
        """获取单篇文章"""
        logging.info(f"获取文章: id={id}")
        post = Post.query.filter_by(id=id, deleted=False).first_or_404()
        return success(data=post.to_json())

    def delete(self, id):
        p = Post.query.filter_by(id=id, deleted=False).first()
        if not p:
            logging.warning(f"用户 {current_user.username} 尝试删除不存在的文章 {id}")
            return error(404, "文章不存在")
        PostItemApi.soft_delete(p)
        # 移除文章缓存
        cache.delete_memoized(PostGroupApi.query_post)
        return success(message="文章删除成功")

    def patch(self, id):
        logging.info(f"编辑文章: id={id}")
        post = Post.query.get_or_404(id)
        if current_user.username != post.author.username and not current_user.can(
            Permission.ADMIN
        ):
            logging.warning(f"用户 {current_user.username} 尝试编辑不属于自己的文章 {id}")
            return error(403, "没有权限编辑此文章")

        # 对表单编辑业务逻辑
        j = request.get_json()
        post.body = j.get("body", post.body)
        post.body_html = j.get("bodyHtml") if j.get("bodyHtml") else None
        db.session.add(post)
        # 编辑markdown文章时新增图片
        images = j.get("images")
        if images:
            images = [
                Image(
                    url=image.get("url", ""),
                    type=ImageType.POST,
                    describe=image.get("pos", ""),
                    related_id=post.id,
                )
                for image in images
            ]
            db.session.add_all(images)
        db.session.commit()
        return success(data=post.to_json())


class PostGroupApi(DecoratedMethodView):
    method_decorators = {
        # "get": [log_operate],
        "get": [sql_profile],
        "post": [jwt_required()],
    }

    # @cache.memoize(timeout=60)
    @staticmethod
    def query_post(page, per_page, tab_name=None):
        if tab_name and tab_name == "showFollowed":
            base_query = current_user.followed_posts
        else:
            base_query = Post.query.filter_by(deleted=False)

        # 主查询：预加载作者信息
        query = base_query.options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        ).order_by(Post.timestamp.desc())

        # 分页查询
        paginate = query.paginate(page=page, per_page=per_page, error_out=False)
        posts = paginate.items

        if not posts:
            return [], paginate.total

        # 获取文章ID列表
        post_ids = [post.id for post in posts]

        # 子查询1：获取所有文章图片
        images_query = (
            db.session.query(Image.related_id, Image.url, Image.describe, Image.id)
            .filter(Image.type == ImageType.POST, Image.related_id.in_(post_ids))
            .order_by(Image.related_id.asc(), Image.id.asc())
            .all()
        )

        # 子查询2：获取评论数量
        comments_count_query = (
            db.session.query(
                Comment.post_id, func.count(Comment.id).label("comment_count")
            )
            .filter(Comment.post_id.in_(post_ids))
            .group_by(Comment.post_id)
            .all()
        )

        # 子查询3：获取点赞数量
        praise_count_query = (
            db.session.query(
                Praise.post_id, func.count(Praise.id).label("praise_count")
            )
            .filter(Praise.post_id.in_(post_ids))
            .group_by(Praise.post_id)
            .all()
        )

        # 子查询4：获取当前用户的点赞状态（如果用户已登录）
        user_praised_dict = {}
        if current_user:
            user_praised_query = (
                db.session.query(Praise.post_id)
                .filter(
                    Praise.post_id.in_(post_ids), Praise.author_id == current_user.id
                )
                .all()
            )
            user_praised_dict = {post_id: True for post_id, in user_praised_query}

        # 整理数据为字典格式便于查找
        images_dict = {}
        for image in images_query:
            if image.related_id not in images_dict:
                images_dict[image.related_id] = []
            images_dict[image.related_id].append(
                {
                    "url": get_avatars_url(image.url),
                    "describe": image.describe,
                    "id": image.id,
                }
            )

        comments_count_dict = {
            post_id: count for post_id, count in comments_count_query
        }
        praise_count_dict = {post_id: count for post_id, count in praise_count_query}

        # 构建返回数据
        result = []
        for post in posts:
            images_data = images_dict.get(post.id, [])
            urls = [img["url"] for img in images_data]
            pos = [img["describe"] for img in images_data]

            body = post.body
            body_html = post.body_html

            if post.type == PostType.IMAGE:
                if post.body_html:
                    body = Post.replace_body(post.body, pos, urls)
                    body_html = Post.replace_body_html(post.body_html, pos, urls)

            json_post = {
                "id": post.id,
                "body": body,
                "body_html": body_html,
                "post_images": urls if not post.body_html else [],
                "pos": pos,
                "post_type": post.type.value,
                "timestamp": post.timestamp
                if isinstance(post.timestamp, str)
                else DateUtils.datetime_to_str(post.timestamp),
                "author": post.author.username,
                "nick_name": post.author.nickname,
                "user_id": post.author.id,
                "comment_count": comments_count_dict.get(post.id, 0),
                "image": get_avatars_url(post.author.image),
                "praise_num": praise_count_dict.get(post.id, 0),
                "has_praised": user_praised_dict.get(post.id, False),
            }
            result.append(json_post)

        return result, paginate.total

    @staticmethod
    def new_post_notification(post_id):
        """创建新文章通知并推送给粉丝"""
        # 批量查询当前用户的所有粉丝（排除自己）
        followers = (
            Follow.query.filter_by(followed_id=current_user.id)
            .filter(Follow.follower_id != current_user.id)
            .all()
        )

        if not followers:
            return

        # 批量创建通知
        notifications = [
            Notification(
                receiver_id=follow.follower_id,
                trigger_user_id=current_user.id,
                post_id=post_id,
                type=NotificationType.NewPost,
            )
            for follow in followers
        ]
        db.session.add_all(notifications)
        db.session.commit()

        # 批量推送通知
        for notification in notifications:
            socketio.emit(
                "new_notification",
                notification.to_json(),
                to=str(notification.receiver_id),
            )

    @staticmethod
    def submit_to_db(post_type, body, body_html, images=None):
        try:
            post = Post(
                body=body, body_html=body_html, type=post_type, author=current_user
            )
            db.session.add(post)
            db.session.flush()
            # images：  [ '', '' ] or [ {'url':'', 'pos':''},{} ]
            # markdown
            if images and isinstance(images[0], dict):
                images = [
                    Image(
                        url=image.get("url", ""),
                        type=ImageType.POST,
                        describe=image.get("pos", ""),
                        related_id=post.id,
                    )
                    for image in images
                ]
                db.session.add_all(images)
            # 图文
            elif images and isinstance(images[0], str):
                images = [
                    Image(url=image, type=ImageType.POST, related_id=post.id)
                    for image in images
                ]
                db.session.add_all(images)
            db.session.commit()
            PostGroupApi.new_post_notification(post.id)
            logging.info(f"创建新文章: user_id={current_user.id}, post_id={post.id}")
        except Exception as e:
            logging.error(f"创建文章失败: {str(e)}", exc_info=True)
            db.session.rollback()
            raise f"创建文章失败: {str(e)}"

    @staticmethod
    def posts_publish(data: dict):
        body = data.get("body", "")
        body_html = data.get("bodyHtml", None)
        images = data.get("images", [])
        # 可选text, image, markdown
        post_type = data.get("type", "text")
        match post_type:
            case "text":
                PostGroupApi.submit_to_db(PostType.TEXT, body, body_html, images)
            case "image":
                PostGroupApi.submit_to_db(PostType.IMAGE, body, body_html, images)
            case "markdown":
                limiter.limit("2/day", exempt_when=lambda: current_user.role_id == 3)
                PostGroupApi.submit_to_db(PostType.IMAGE, body, body_html, images)

    def get(self):
        """获取所有文章"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["FLASKY_POSTS_PER_PAGE"], type=int
        )
        posts, total = PostGroupApi.query_post(
            page, per_page, request.args.get("tabName")
        )
        return success(data=posts, total=total)

    def post(self):
        """发布文章"""
        if current_user.can(Permission.WRITE):
            try:
                PostGroupApi.posts_publish(request.json)
                # 清除缓存
                cache.delete_memoized(PostGroupApi.query_post)
            except Exception as e:
                return error(500, f"{str(e)}")
            posts, total = PostGroupApi.query_post(
                1, current_app.config["FLASKY_POSTS_PER_PAGE"]
            )
            return success(data=posts, total=total)


def register_post_api(bp, *, post_item_url, post_group_url):
    item = PostItemApi.as_view("post_item")
    group = PostGroupApi.as_view("post_group")
    bp.add_url_rule(post_item_url, view_func=item)
    bp.add_url_rule(post_group_url, view_func=group)
