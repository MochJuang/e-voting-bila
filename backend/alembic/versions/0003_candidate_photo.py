"""add candidate photo column

Revision ID: 0003_candidate_photo
Revises: 0002_face_photo_snapshot
Create Date: 2026-08-01 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import MEDIUMTEXT


# revision identifiers, used by Alembic.
revision = "0003_candidate_photo"
down_revision = "0002_face_photo_snapshot"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "candidates",
        sa.Column("photo_base64", sa.Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("candidates", "photo_base64")
