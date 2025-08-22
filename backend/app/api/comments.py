from flask import request, url_for, current_app
from .. import db
from ..models import Post, Permission, Comment, Praise
from . import api
from .decorators import permission_required
from ..utils.response import success, error, not_found
from .. import logger

# 日志
log = logger.get_logger()

@api.route('/comments/')
def get_comments():
    """
    获取所有评论
    ---
    tags:
      - 评论
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: 页码
    responses:
      200:
        description: 成功获取评论列表
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
                comments:
                  type: array
                  items:
                    type: object
                prev:
                  type: string
                  example: /api/v1/comments?page=1
                next:
                  type: string
                  example: /api/v1/comments?page=3
                count:
                  type: integer
                  example: 100
    """
    log.info("获取评论列表")
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page + 1)
    return success(data={
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/comments/<int:id>')
def get_comment(id):
    """
    获取指定评论
    ---
    tags:
      - 评论
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: 评论ID
    responses:
      200:
        description: 成功获取评论
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
        description: 评论不存在
    """
    log.info(f"获取评论: id={id}")
    comment = Comment.query.get_or_404(id)
    return success(data=comment.to_json())


@api.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(id):
    """
    创建新评论
    ---
    tags:
      - 评论
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
              description: 评论内容
    responses:
      200:
        description: 成功创建评论
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
    log.info(f"创建新评论: post_id={id}")
    post = Post.query.get_or_404(id)
    try:
        comment = Comment.from_json(request.json)
        comment.author = g.current_user
        comment.post = post
        db.session.add(comment)
        db.session.commit()
        return success(
            data=comment.to_json(),
            message="评论创建成功"
        )
    except Exception as e:
        log.error(f"创建评论失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"创建评论失败: {str(e)}")


@api.route('/posts/<int:id>/comments/')
def get_comments_new(id):
    """
    获取文章的根评论及第一层回复
    ---
    tags:
      - 评论
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: 文章ID
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: 页码
      - name: size
        in: query
        type: integer
        required: false
        description: 每页数量
    responses:
      200:
        description: 成功获取评论列表
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
      404:
        description: 文章不存在
    """
    log.info(f"获取文章评论: post_id={id}")
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('size', current_app.config['FLASKY_COMMENTS_PER_PAGE'], type=int)
    # 获取根评论分页（parent_comment_id为None）
    root_comments_pagination = post.comments.filter(Comment.root_comment_id.is_(None)).order_by(
        Comment.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)

    comments = []
    for root_comment in root_comments_pagination.items:
        comment_data = root_comment.to_json_new()
        # 获取该根评论下的第一层直接回复（direct_parent_id=根评论ID）
        first_level_replies, reply_total = get_replies_by_parent(root_comment.id, page=1)
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


@api.route('/reply_comments/')
def get_comment_replies():
    """
    获取指定评论的回复分页
    ---
    tags:
      - 评论
    parameters:
      - name: rootCommentId
        in: query
        type: integer
        required: true
        description: 根评论ID
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: 页码
    responses:
      200:
        description: 成功获取评论回复
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
    """
    log.info("获取评论回复")
    root_comment_id = request.args.get('rootCommentId', type=int)
    page = request.args.get('page', 1, type=int)
    # 分页时不自动嵌套，前端按需请求
    replies, total = get_replies_by_parent(root_comment_id=root_comment_id, page=page)

    return success(
        data=replies, 
        extra={
            'total': total, 
            'current_page': page
        }
    )
