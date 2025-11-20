import os
import logging

from celery import shared_task
from flask import render_template
from flask_mail import Message

from .. import mail, db
from ..models import Post, Image, ImageType
from ..utils.response import error
from ..main.uploads import del_qiniu_image


@shared_task(ignore_result=False)
def send_email(to, subject, template, **kwargs):
    try:
        message = Message(subject=subject, recipients=[to])
        message.html = render_template(template, **kwargs)
        mail.send(message)
    except Exception as e:
        print(e)
        print("发送失败")


@shared_task(ignore_result=False)
def hard_delete():
    try:
        # 直接获取需要删除的文章ID，避免加载完整的Post对象
        posts_query = Post.query.filter_by(deleted=True)
        post_count = posts_query.count()

        if post_count == 0:
            logging.info("Celery: 没有需要删除的文章")
            return

        post_ids = [p.id for p in posts_query.with_entities(Post.id).all()]
        logging.info(f"Celery: 开始删除文章，共 {post_count} 篇")

        # 直接查询图片URL，避免加载完整的Image对象
        image_urls = (
            Image.query.with_entities(Image.url)
            .filter(Image.type == ImageType.POST, Image.related_id.in_(post_ids))
            .all()
        )

        # image_urls格式: [('dev/bdb625d5-5237-43a5-8bc9-af826693d166.jpg',),
        # ('dev/e1a1b72c-8bba-4267-9ab7-0b0394fe7e45.jpg',)]
        all_image_urls = [url[0] for url in image_urls]

        # 批量删除云存储图片
        if all_image_urls:
            data = {
                "bucket_name": os.getenv("QINIU_BUCKET_NAME", ""),
                "keys": all_image_urls,
            }
            del_qiniu_image(**data)
            logging.info(f"七牛云批量删除图片成功，共 {len(all_image_urls)} 张")

        # 批量删除文章
        # synchronize_session=False 告诉 SQLAlchemy 不要同步当前 session 中的对象状态
        post_delete_result = posts_query.delete(synchronize_session=False)

        db.session.commit()
        logging.info(f"批量删除完成：删除文章 {post_delete_result} 篇（含关联图片）")

    except Exception as e:
        logging.error(f"批量删除文章失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return error(500, f"批量删除文章失败: {str(e)}")
