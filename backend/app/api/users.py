from flask import request, current_app, url_for
from . import api
from ..models import User, Post, Follow
from flask_jwt_extended import current_user, jwt_required
from .. import db
from ..utils.common import get_avatars_url
from ..utils.response import success, error, not_found
from .. import logger


@api.route('/users/<int:id>')
def get_user(id):
    """
    获取用户信息
    ---
    tags:
      - 用户
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: 用户ID
    responses:
      200:
        description: 成功获取用户信息
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
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: test_user
      404:
        description: 用户不存在
        schema:
          properties:
            code:
              type: integer
              example: 404
            message:
              type: string
              example: 资源不存在
            data:
              type: object
              example: {}
    """
    logger.get_logger().info(f"获取用户信息: id={id}")
    user = User.query.get_or_404(id)
    return success(data=user.to_json())


@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    logger.get_logger().info(f"获取用户文章: id={id}")
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page + 1)
    return success(data={
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    logger.get_logger().info(f"获取用户关注的文章: id={id}")
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', id=id, page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_followed_posts', id=id, page=page + 1)
    return success(data={
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


# 在关注列表中，根据用户昵称或者账号搜索
@api.route('/search_followed', methods=['GET'])
def search_followed():
    """
    搜索关注的用户
    ---
    tags:
      - 用户关系
    parameters:
      - name: name
        in: query
        type: string
        required: false
        description: 搜索关键词
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer {token}
    responses:
      200:
        description: 成功获取关注用户列表
        schema:
          properties:
            code:
              type: integer
              example: 200
            message:
              type: string
              example: success
            data:
              type: array
              items:
                type: object
                properties:
                  username:
                    type: string
                    example: user123
                  image:
                    type: string
                    example: http://example.com/avatar.jpg
      404:
        description: 用户不存在
        schema:
          properties:
            code:
              type: integer
              example: 404
            message:
              type: string
              example: 用户不存在
            data:
              type: object
              example: {}
    """
    search_query = request.args.get('name', '').strip()
    logger.get_logger().info(f"搜索关注用户: query={search_query}")
    # 关注者
    user = User.query.filter_by(username=current_user.username).first()
    if not user:
        return error(404, "用户不存在")

    followed_user_ids = user.followed.with_entities(Follow.followed_id).all()
    followed_user_ids = [item[0] for item in followed_user_ids]
    # 搜索用户名或账号
    followed_users = User.query.filter(
        User.id.in_(followed_user_ids),
        db.or_(
            User.username.ilike(f'%{search_query}%'),
            User.nickname.ilike(f'%{search_query}%')
        )
    ).all()
    follows = [{'username': item.username, 'image': get_avatars_url(item.image)}
               for item in followed_users if item.username != user.username]
    return success(data=follows)


@api.route('/search_fan', methods=['GET'])
def search_fan():
    search_query = request.args.get('name', '').strip()
    logger.get_logger().info(f"搜索粉丝: query={search_query}")
    # 粉丝
    user = User.query.filter_by(username=current_user.username).first()
    if not user:
        return error(404, "用户不存在")

    followed_user_ids = user.followers.with_entities(Follow.follower_id).all()
    followed_user_ids = [item[0] for item in followed_user_ids]
    # 搜索用户名或账号
    followed_users = User.query.filter(
        User.id.in_(followed_user_ids),
        db.or_(
            User.username.ilike(f'%{search_query}%'),
            User.nickname.ilike(f'%{search_query}%')
        )
    ).all()
    follows = [{'username': item.username, 'image': get_avatars_url(item.image)}
               for item in followed_users if item.username != user.username]
    return success(data=follows)


@api.route('/update_user', methods=['POST'])
@jwt_required()
def update_user_profile():
    """
    更新用户信息
    ---
    tags:
      - 用户
    parameters:
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
            nickname:
              type: string
              description: 用户昵称
            about_me:
              type: string
              description: 个人简介
            location:
              type: string
              description: 位置
    responses:
      200:
        description: 用户信息更新成功
        schema:
          properties:
            code:
              type: integer
              example: 200
            message:
              type: string
              example: 用户信息更新成功
            data:
              type: object
              example: {}
      500:
        description: 服务器错误
        schema:
          properties:
            code:
              type: integer
              example: 500
            message:
              type: string
              example: 更新用户信息失败
            data:
              type: object
              example: {}
    """
    logger.get_logger().info(f"更新用户信息: user_id={current_user.id}")
    try:
        for key, value in request.json.items():
            if hasattr(current_user, key):
                setattr(current_user, key, value)
        db.session.commit()
        return success(message="用户信息更新成功")
    except Exception as e:
        logger.get_logger().error(f"更新用户信息失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"更新用户信息失败: {str(e)}")
