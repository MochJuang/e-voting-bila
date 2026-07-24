from sqlalchemy import ForeignKey, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import VerificationResult, sqlalchemy_enum
from app.models.mixins import IdMixin, TimestampMixin


class FaceVerificationLog(Base, IdMixin, TimestampMixin):
    __tablename__ = "face_verification_logs"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    result: Mapped[VerificationResult] = mapped_column(
        sqlalchemy_enum(VerificationResult, name="verification_result"), nullable=False
    )
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    liveness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    device_info: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="verification_logs")
