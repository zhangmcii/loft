import os

from dns.rdtypes.svcbbase import NoDefaultALPNParam
from flask import request, current_app
from .decorators import DecoratedMethodView
from ..decorators import log_operate
from flask_jwt_extended import jwt_required, verify_jwt_in_request, current_user
from .. import db
from ..models import Post, Permission, Follow, Image, ImageType, PostType, Notification, NotificationType
from ..main.uploads import del_qiniu_image
from ..utils.response import success, error
from .. import socketio
from .. import logger
from .. import limiter

# 日志
log = logger.get_logger()


class PostItemApi(DecoratedMethodView):
    method_decorators = {
        'get': [],
        'delete': [jwt_required()],
        'patch': [jwt_required()]
    }

    def get(self, id):
        """获取单篇文章"""
        log.info(f"获取文章: id={id}")
        post = Post.query.get_or_404(id)
        return success(data=post.to_json())

    def delete(self, id):
        log.info(f"删除文章: id={id}")
        # 删除文章，同时也要删除文章中的图片url
        is_contain_image, data = None, None
        try:
            p = Post.query.filter_by(id=id, author_id=current_user.id).first()
            if not p:
                log.warning(f"用户 {current_user.username} 尝试删除不存在的文章 {id}")
                return error(404, "文章不存在")

            is_contain_image = p.type == PostType.IMAGE
            to_del_urls = []
            if is_contain_image:
                post_images = Image.query.filter(Image.type == ImageType.POST, Image.related_id == p.id).order_by(
                    Image.id.asc()).all()
                to_del_urls = [image.url for image in post_images]
                # 删除图片
                data = {'bucket_name': os.getenv('QINIU_BUCKET_NAME', ''), 'keys': to_del_urls}
            db.session.delete(p)
            db.session.commit()
        except Exception as e:
            log.error(f"删除文章失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"删除文章失败: {str(e)}")

        if is_contain_image and to_del_urls:
            # 传递j,执行图片删除
            del_qiniu_image(**data)
        return success(message="文章删除成功")

    def patch(self, id):
        log.info(f"编辑文章: id={id}")
        post = Post.query.get_or_404(id)
        if current_user.username != post.author.username and not current_user.can(Permission.ADMIN):
            log.warning(f"用户 {current_user.username} 尝试编辑不属于自己的文章 {id}")
            return error(403, "没有权限编辑此文章")

        # 对表单编辑业务逻辑
        j = request.get_json()
        post.body = j.get('body', post.body)
        post.body_html = j.get('bodyHtml') if j.get('bodyHtml') else None
        db.session.add(post)
        # 编辑markdown文章时新增图片
        images = j.get('images')
        if images:
            images = [
                Image(url=image.get('url', ''), type=ImageType.POST, describe=image.get('pos', ''), related_id=post.id)
                for image in images]
            db.session.add_all(images)
        db.session.commit()
        return success(data=post.to_json())


class PostGroupApi(DecoratedMethodView):
    method_decorators = {
        'get': [log_operate],
        'post': [jwt_required()],
    }

    @staticmethod
    def query_post(page, per_page, tab_name=None):
        if tab_name and tab_name == "showFollowed":
            query = current_user.followed_posts
        else:
            query = Post.query
        paginate = query.order_by(Post.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        posts = paginate.items
        return [post.to_json() for post in posts], query.count()

    @staticmethod
    def new_post_notification(post_id):
        """创建新文章通知并推送给粉丝"""
        # 查询当前用户的所有粉丝（排除自己）
        followers = Follow.query.filter_by(followed_id=current_user.id).all()

        # 为每个粉丝创建通知并推送
        for follow in followers:
            # 跳过作者自己（虽然逻辑上自己不会关注自己，但以防万一）
            if follow.follower_id == current_user.id:
                continue

            # 创建通知
            notification = Notification(
                receiver_id=follow.follower_id,  # 粉丝ID
                trigger_user_id=current_user.id,  # 触发用户（作者）
                post_id=post_id,  # 关联文章ID
                type=NotificationType.NewPost,  # 通知类型：新文章
            )
            db.session.add(notification)
            db.session.flush()  # 刷新以获取通知ID

            # 实时推送给粉丝
            socketio.emit(
                "new_notification",
                notification.to_json(),
                to=str(follow.follower_id),  # 发送到粉丝的房间
            )

        # 提交所有通知
        db.session.commit()

    @staticmethod
    def submit_to_db(post_type, body, body_html, images=None):
        try:
            post = Post(body=body, body_html=body_html, type=post_type, author=current_user)
            db.session.add(post)
            db.session.flush()
            if images:
                images = [
                    Image(url=image.get("url", ""), type=ImageType.POST, describe=image.get("pos", ""),
                          related_id=post.id)
                    for image in images]
                db.session.add_all(images)
            db.session.commit()
            PostGroupApi.new_post_notification(post.id)
            log.info(f"创建新文章: user_id={current_user.id}, post_id={post.id}")
        except Exception as e:
            log.error(f"创建文章失败: {str(e)}", exc_info=True)
            db.session.rollback()
            raise f"创建文章失败: {str(e)}"

    @staticmethod
    def posts_publish(data: dict):
        body = data.get("body", '')
        body_html = data.get("bodyHtml", None)
        images = data.get("images", [])
        # 可选text, image, markdown
        post_type = data.get('type', 'text')
        match post_type:
            case 'text':
                PostGroupApi.submit_to_db(PostType.TEXT, body, body_html, images)
            case 'image':
                PostGroupApi.submit_to_db(PostType.IMAGE, body, body_html, images)
            case 'markdown':
                limiter.limit("2/day", exempt_when=lambda: current_user.role_id == 3)
                PostGroupApi.submit_to_db(PostType.IMAGE, body, body_html, images)

    def get(self):
        """获取所有文章"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["FLASKY_POSTS_PER_PAGE"], type=int
        )
        posts, total = PostGroupApi.query_post(page, per_page, request.args.get("tabName"))
        return success(data=posts, total=total)

    def post(self):
        """发布文章"""
        if current_user.can(Permission.WRITE):
            try:
                PostGroupApi.posts_publish(request.json)
            except Exception as e:
                return error(500, f"{str(e)}")
            posts, total = PostGroupApi.query_post(1, current_app.config["FLASKY_POSTS_PER_PAGE"])
            return success(data=posts, total=total)


def register_post_api(bp, *, post_item_url, post_group_url):
    item = PostItemApi.as_view('post_item')
    group = PostGroupApi.as_view('post_group')
    bp.add_url_rule(post_item_url, view_func=item)
    bp.add_url_rule(post_group_url, view_func=group)
