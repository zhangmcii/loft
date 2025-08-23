import os

from flask import request, url_for, current_app, abort
from flask_jwt_extended import current_user, jwt_required
from .. import db
from ..models import Post, Permission, Image, ImageType, PostType
from . import api
from ..main.uploads import del_qiniu_image
from ..utils.response import success, error
from .. import logger

# 日志
log = logger.get_logger()

@api.route('/posts/')
def get_posts():
    """
    获取所有文章
    ---
    tags:
      - 文章
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: 页码
    responses:
      200:
        description: 成功获取文章列表
        schema:
          properties:
            code:
              type: integer
              example: 200
            message:
              type: string
              example: success
            data:
              type: object
              properties:
                posts:
                  type: array
                  items:
                    type: object
                prev:
                  type: string
                  example: /api/v1/posts?page=1
                next:
                  type: string
                  example: /api/v1/posts?page=3
                count:
                  type: integer
                  example: 100
    """
    log.info("获取文章列表")
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page + 1)
    return success(data={
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/posts/<int:id>')
def get_post(id):
    """
    获取指定文章
    ---
    tags:
      - 文章
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: 文章ID
    responses:
      200:
        description: 成功获取文章
        schema:
          properties:
            code:
              type: integer
              example: 200
            message:
              type: string
              example: success
            data:
              type: object
      404:
        description: 文章不存在
    """
    log.info(f"获取文章: id={id}")
    post = Post.query.get_or_404(id)
    return success(data=post.to_json())


@api.route('/posts/<int:id>', methods=['PUT'])
@jwt_required()
def edit_post(id):
    """
    编辑文章
    ---
    tags:
      - 文章
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: 文章ID
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer {token}
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            body:
              type: string
              description: 文章内容
            bodyHtml:
              type: string
              description: HTML格式的文章内容
            images:
              type: array
              items:
                type: object
                properties:
                  url:
                    type: string
                  pos:
                    type: string
    responses:
      200:
        description: 成功编辑文章
        schema:
          properties:
            code:
              type: integer
              example: 200
            message:
              type: string
              example: success
            data:
              type: object
      403:
        description: 没有权限编辑
      404:
        description: 文章不存在
    """
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


@api.route('/posts/<int:id>', methods=['DELETE'])
@jwt_required()
def del_post(id):
    """
    删除文章
    ---
    tags:
      - 文章
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: 文章ID
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer {token}
    responses:
      200:
        description: 成功删除文章
        schema:
          properties:
            code:
              type: integer
              example: 200
            message:
              type: string
              example: success
            data:
              type: object
              example: {}
      400:
        description: 删除失败
        schema:
          properties:
            code:
              type: integer
              example: 400
            message:
              type: string
              example: 文章不存在
            data:
              type: object
              example: {}
    """
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
