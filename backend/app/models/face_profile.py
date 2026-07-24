from sqlalchemy import ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class FaceProfile(Base, IdMixin, TimestampMixin):
    __tablename__ = "face_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    embedding: Mapped[bytes] = mapped_column(LargeBinary(length=65535), nullable=False)
    embedding_version: Mapped[str] = mapped_column(String(50), nullable=False, default="insightface-v1")
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="face_profiles")

