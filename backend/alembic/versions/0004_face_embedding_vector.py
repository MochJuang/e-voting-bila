"""add face_profiles.embedding_vector (JSON, human-readable mirror of embedding blob)

Revision ID: 0004_face_embedding_vector
Revises: 0003_candidate_photo
Create Date: 2026-08-02 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0004_face_embedding_vector"
down_revision = "0003_candidate_photo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "face_profiles",
        sa.Column("embedding_vector", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("face_profiles", "embedding_vector")
