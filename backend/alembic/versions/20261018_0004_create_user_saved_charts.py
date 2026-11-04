"""create user saved charts table

Revision ID: 20261018_0004
Revises: 20260825_0003
Create Date: 2026-10-18
"""
from alembic import op
import sqlalchemy as sa

revision = "20261018_0004"
down_revision = "20260825_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_saved_charts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("person_name", sa.String(length=120), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("birth_date", sa.String(length=20), nullable=False),
        sa.Column("birth_time", sa.String(length=20), nullable=False),
        sa.Column("birth_city", sa.String(length=120), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("timezone_offset", sa.Float(), nullable=False, server_default="5.5"),
        sa.Column("tz_name", sa.String(length=64), nullable=True),
        sa.Column("ayanamsa", sa.String(length=40), nullable=False, server_default="Lahiri"),
        sa.Column("chart_data", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_saved_charts_id"), "user_saved_charts", ["id"], unique=False)
    op.create_index(op.f("ix_user_saved_charts_user_id"), "user_saved_charts", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_saved_charts_created_at"), "user_saved_charts", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_saved_charts_created_at"), table_name="user_saved_charts")
    op.drop_index(op.f("ix_user_saved_charts_user_id"), table_name="user_saved_charts")
    op.drop_index(op.f("ix_user_saved_charts_id"), table_name="user_saved_charts")
    op.drop_table("user_saved_charts")
