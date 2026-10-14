"""用户背景增加 ThumbHash 占位字段

Revision ID: e5b72d19c4a1
Revises: da589f891f75
Create Date: 2026-10-15 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "e5b72d19c4a1"
down_revision = "da589f891f75"


def upgrade():
    op.add_column(
        "users", sa.Column("bg_image_lqip", sa.String(length=128), nullable=True)
    )
    op.add_column(
        "users", sa.Column("pc_bg_image_lqip", sa.String(length=128), nullable=True)
    )


def downgrade():
    op.drop_column("users", "pc_bg_image_lqip")
    op.drop_column("users", "bg_image_lqip")
