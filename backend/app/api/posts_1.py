import os
from email.headerregistry import Group

from flask import request, current_app
from flask.views import MethodView
from flask_jwt_extended import current_user
from .. import db
from ..models import Post, Permission, Image, ImageType, PostType
from ..main.uploads import del_qiniu_image
from ..utils.response import success, error
from .. import logger
from ..main.notifications import new_post_notification

# 日志
log = logger.get_logger()


class PostItemApi(MethodView):

    def __init__(self):
        pass

    def get(self, id):
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


class PostGroupApi(MethodView):
    def __init__(self):
        pass

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

    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["FLASKY_POSTS_PER_PAGE"], type=int
        )
        posts, total = PostGroupApi.query_post(page, per_page, request.args.get("tabName"))
        return success(data=posts, total=total)

    def post(self):
        if current_user.can(Permission.WRITE):
            try:
                j = request.get_json()
                body_html = j.get("bodyHtml")
                images = j.get("images")
                post = Post(
                    body=j.get("body"),
                    body_html=body_html if body_html else None,
                    type=PostType.IMAGE if body_html else PostType.TEXT,
                    author=current_user,
                )
                db.session.add(post)
                db.session.flush()
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
                new_post_notification(post.id)
                log.info(
                    f"创建新文章: user_id={current_user.id}, post_id={post.id}"
                )
            except Exception as e:
                log.error(f"创建文章失败: {str(e)}", exc_info=True)
                db.session.rollback()
                return error(500, f"创建文章失败: {str(e)}")

        posts, total = PostGroupApi.query_post(1, current_app.config["FLASKY_POSTS_PER_PAGE"])
        return success(data=posts, total=total)


def register_bp_api(bp, name):
    item = PostItemApi.as_view(f'{name}_item')
    group = PostGroupApi.as_view(f'{name}_group')
    bp.add_url_rule(f'/{name}/<int:id>', view_func=item)
    bp.add_url_rule(f'/{name}', view_func=group)
