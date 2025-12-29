"""对文章关联的评论、点赞, 评论关联的点赞模型添加删除级联

Revision ID: 834d2f86ae28
Revises: 9a2c956701e0
Create Date: 2025-12-29 15:28:01.861451

"""

# revision identifiers, used by Alembic.
revision = "834d2f86ae28"
down_revision = "9a2c956701e0"

from alembic import op


def upgrade():
    # ===== comments =====
    op.drop_constraint("comments_ibfk_2", "comments", type_="foreignkey")
    op.drop_constraint("comments_ibfk_3", "comments", type_="foreignkey")
    op.drop_constraint("comments_ibfk_4", "comments", type_="foreignkey")

    op.create_foreign_key(
        "fk_comments_post_id_posts",
        "comments",
        "posts",
        ["post_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_comments_direct_parent_id_comments",
        "comments",
        "comments",
        ["direct_parent_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_comments_root_comment_id_comments",
        "comments",
        "comments",
        ["root_comment_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ===== notifications =====
    op.drop_constraint("notifications_ibfk_3", "notifications", type_="foreignkey")
    op.drop_constraint("notifications_ibfk_4", "notifications", type_="foreignkey")

    op.create_foreign_key(
        "fk_notifications_post_id_posts",
        "notifications",
        "posts",
        ["post_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 先清洗数据，再加外键
    op.execute("""
        UPDATE notifications
        SET comment_id = NULL
        WHERE comment_id IS NOT NULL
        AND comment_id NOT IN (SELECT id FROM comments)
    """)
    op.create_foreign_key(
        "fk_notifications_comment_id_comments",
        "notifications",
        "comments",
        ["comment_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ===== praise =====
    op.drop_constraint("praise_ibfk_2", "praise", type_="foreignkey")
    op.drop_constraint("praise_ibfk_3", "praise", type_="foreignkey")

    op.create_foreign_key(
        "fk_praise_comment_id_comments",
        "praise",
        "comments",
        ["comment_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_praise_post_id_posts",
        "praise",
        "posts",
        ["post_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    # ===== comments =====
    op.drop_constraint("fk_comments_post_id_posts", "comments", type_="foreignkey")
    op.drop_constraint(
        "fk_comments_direct_parent_id_comments", "comments", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_comments_root_comment_id_comments", "comments", type_="foreignkey"
    )

    op.create_foreign_key("comments_ibfk_2", "comments", "posts", ["post_id"], ["id"])

    op.create_foreign_key(
        "comments_ibfk_3", "comments", "comments", ["direct_parent_id"], ["id"]
    )

    op.create_foreign_key(
        "comments_ibfk_4", "comments", "comments", ["root_comment_id"], ["id"]
    )

    # ===== notifications =====
    op.drop_constraint(
        "fk_notifications_post_id_posts", "notifications", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_notifications_comment_id_comments", "notifications", type_="foreignkey"
    )

    op.create_foreign_key(
        "notifications_ibfk_3", "notifications", "posts", ["post_id"], ["id"]
    )

    op.create_foreign_key(
        "notifications_ibfk_4", "notifications", "comments", ["comment_id"], ["id"]
    )

    # ===== praise =====
    op.drop_constraint("fk_praise_comment_id_comments", "praise", type_="foreignkey")
    op.drop_constraint("fk_praise_post_id_posts", "praise", type_="foreignkey")

    op.create_foreign_key("praise_ibfk_2", "praise", "posts", ["post_id"], ["id"])

    op.create_foreign_key("praise_ibfk_3", "praise", "comments", ["comment_id"], ["id"])
