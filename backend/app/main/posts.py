# 日志
import logging

from flask import current_app, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm import joinedload

from .. import db, limiter
from ..models import Image, ImageType, Permission, Post, PostType, User
from ..utils.response import error, forbidden, not_found, success
from ..mycelery.notification_task import create_new_post_notifications
from . import main


# --------------------------- 博客文章 ---------------------------
@main.route("/", methods=["GET", "POST"])
def index():
    """处理博客文章的首页路由"""
    if request.method == "POST" and current_user.can(Permission.WRITE):
        try:
            j = request.get_json()
            images = j.get("images")
            post_type = j.get("type", "text")
            # 根据type字段确定PostType
            if post_type == "markdown":
                post_type_enum = PostType.MARKDOWN
            elif post_type == "image":
                post_type_enum = PostType.TEXT  # 图文使用TEXT类型，通过has_image区分
            else:
                post_type_enum = PostType.TEXT
                
            post = Post(
                content=j.get("content"),
                type=post_type_enum,
                has_image=bool(images),  # 如果有图片则设置has_image为True
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

            # 异步创建新文章通知
            from ..models import Follow

            followers = (
                Follow.query.filter_by(followed_id=current_user.id)
                .filter(Follow.follower_id != current_user.id)
                .all()
            )
            follower_ids = [follow.follower_id for follow in followers]
            create_new_post_notifications.delay(post.id, current_user.id, follower_ids)

            logging.info(f"创建新文章: user_id={current_user.id}, post_id={post.id}")
        except Exception as e:
            logging.error(f"创建文章失败: {str(e)}", exc_info=True)
            db.session.rollback()
            return error(500, f"创建文章失败: {str(e)}")

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get(
        "per_page", current_app.config["FLASKY_POSTS_PER_PAGE"], type=int
    )
    if request.args.get("tabName") == "showFollowed":
        query = current_user.followed_posts
    else:
        query = Post.query.filter_by(deleted=False)

    # 预加载作者信息
    paginate = (
        query.options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        )
        .order_by(Post.timestamp.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    posts = paginate.items

    posts_json = Post.batch_query_with_data(posts)

    return success(data=posts_json, total=query.count())


@main.route("/user/<username>")
@jwt_required(optional=True)
def user(username):
    """根据用户名获取文章的资料页面路由"""
    logging.info(f"获取用户文章: username={username}")
    user = User.query.filter_by(username=username).first()
    if not user:
        return not_found("用户不存在")

    page = request.args.get("page", 1, type=int)
    pagination = (
        user.posts.filter_by(deleted=False)
        .options(
            joinedload(Post.author).load_only(
                User.id, User.username, User.nickname, User.image
            )
        )
        .order_by(Post.timestamp.desc())
        .paginate(
            page=page,
            per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
            error_out=False,
        )
    )
    posts = pagination.items

    posts_json = Post.batch_query_with_data(posts)

    return success(
        data={"posts": posts_json}, total=user.posts.filter_by(deleted=False).count()
    )


@main.route("/edit/<int:id>", methods=["GET", "PUT"])
@jwt_required()
def edit(id):
    """编辑博客文章"""
    logging.info(f"编辑文章: id={id}")
    post = Post.query.get_or_404(id)
    if current_user.username != post.author.username and not current_user.can(
        Permission.ADMIN
    ):
        logging.warning(f"用户 {current_user.username} 尝试编辑不属于自己的文章 {id}")
        return forbidden("没有权限编辑此文章")

    try:
        # 对表单编辑业务逻辑
        j = request.get_json()
        post.content = j.get("content", post.content)
        db.session.commit()
        return success(message="文章编辑成功")
    except Exception as e:
        logging.error(f"编辑文章失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"编辑文章失败: {str(e)}")


@main.route("/rich_post", methods=["POST"])
@limiter.limit("2/day", exempt_when=lambda: current_user.role_id == 3)
@jwt_required()
def create_post():
    """创建富文本文章"""
    data = request.get_json()
    content = data.get("content", "")
    image_urls = data.get("imageUrls", [])
    p = Post(content=content, type=PostType.MARKDOWN, has_image=bool(image_urls), author=current_user)
    db.session.flush()
    images = [
        Image(url=url, type=ImageType.POST, related_id=p.id) for url in image_urls
    ]
    db.session.add_all(images)
    db.session.commit()

    posts_json = Post.batch_query_with_data([p])

    return success(data=posts_json)
