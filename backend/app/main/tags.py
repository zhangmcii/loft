from flask_jwt_extended import jwt_required, current_user
from . import main
from ..models import Tag
from .. import db
from flask import request
from ..utils.response import success
from .. import logger
from ..decorators import admin_required


# 日志
log = logger.get_logger()


# --------------------------- 标签管理 ---------------------------
@main.route("/tags_list")
@jwt_required()
def get_all_tags():
    """获取所有标签"""
    log.info("获取所有标签")
    tags = Tag.query.all()
    return success(data=[tag.name for tag in tags])


@main.route("/update_user_tag", methods=["POST"])
@jwt_required()
def edit_user_tag():
    """更新当前用户标签"""
    log.info(f"更新用户标签: user_id={current_user.id}")
    d = request.get_json()
    tag_add = set(d.get("tagAdd", []))
    tag_remove = set(d.get("tagRemove", []))
    # 添加新的标签
    for tag_name in tag_add:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        current_user.tags.append(tag)

    # 删除被移除的标签
    for tag_name in tag_remove:
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            current_user.tags.remove(tag)
    db.session.commit()
    return success(message="用户标签更新成功")


@main.route("/update_tag", methods=["POST"])
@admin_required
@jwt_required()
def update_tag():
    """更新公共标签库"""
    log.info("更新公共标签库")
    d = request.json
    tag_add = set(d.get("tagAdd", []))
    tag_remove = set(d.get("tagRemove", []))

    # 添加新的标签
    t = [Tag(name=tag) for tag in tag_add if tag]
    if t:
        db.session.add_all(t)

    # 删除Tag表
    if tag_remove:
        tags_to_delete = Tag.query.filter(Tag.name.in_(tag_remove)).all()
        # 逐个删除，触发before_delete事件
        for tag in tags_to_delete:
            db.session.delete(tag)

    db.session.commit()
    return success(message="公共标签库更新成功")