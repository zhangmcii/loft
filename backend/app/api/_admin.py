from flask_jwt_extended import jwt_required
from ..models import Post, PostType, Permission
from ..decorators import permission_required
from ..utils.response import success, error
from .. import db
import logging
from . import api
from ..utils.markdown_truncate import MarkdownTruncator


@api.route("/admin/init-summaries", methods=["POST"])
@jwt_required()
@permission_required(Permission.ADMIN)
def post_init_summary():
    """
    管理员专用：为所有现有文章初始化summary字段
    如果文章的summary为空，则使用get_smart_preview方法生成summary
    """
    try:
        # 查询所有summary为空的文章
        posts_without_summary = Post.query.filter(
            (Post.summary.is_(None)) | (Post.summary == '')
        ).all()
        # posts_without_summary = Post.query.all()

        total_posts = len(posts_without_summary)
        logging.info(f"找到 {total_posts} 篇需要初始化summary的文章")

        if total_posts == 0:
            return success(message="所有文章都已有summary，无需处理", data={"updated_count": 0})

        # 批量更新文章的summary
        updated_count = 0
        for post in posts_without_summary:
            try:
                # 使用body或body_html生成summary
                content = post.body or post.body_html or ""
                is_pure_text = not post.body and post.body_html
                if content:
                    summary = MarkdownTruncator.get_smart_preview(content, is_pure_text)
                    logging.info(f"summary长度: {len(summary)}")
                    post.summary = summary
                    updated_count += 1

                    # 每100篇提交一次，避免内存占用过大
                    if updated_count % 100 == 0:
                        db.session.commit()
                        logging.info(f"已处理 {updated_count}/{total_posts} 篇文章")
                else:
                    logging.warning(f"文章ID {post.id} 没有内容，跳过")

            except Exception as e:
                logging.error(f"处理文章ID {post.id} 时出错: {str(e)}")
                continue

        # 提交剩余的更改
        db.session.commit()
        logging.info(f"成功为 {updated_count} 篇文章初始化了summary字段")

        return success(
            message=f"成功为 {updated_count} 篇文章初始化了summary字段",
            data={"updated_count": updated_count, "total_found": total_posts},
        )

    except Exception as e:
        logging.error(f"初始化summary字段时出错: {str(e)}")
        db.session.rollback()
        return error(500, f"初始化summary字段时出错: {str(e)}")
