"""add face photo & verification snapshot columns

Revision ID: 0002_face_photo_snapshot
Revises: 0001_initial_schema
Create Date: 2026-07-27 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT


# revision identifiers, used by Alembic.
revision = "0002_face_photo_snapshot"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "face_profiles",
        sa.Column("photo_base64", sa.Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=True),
    )
    op.add_column(
        "face_verification_logs",
        sa.Column("snapshot_base64", sa.Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("face_verification_logs", "snapshot_base64")
    op.drop_column("face_profiles", "photo_base64")
