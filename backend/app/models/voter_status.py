from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class VoterStatus(Base, IdMixin, TimestampMixin):
    __tablename__ = "voter_statuses"
    __table_args__ = (
        UniqueConstraint("user_id", "session_id", name="uq_voter_status_user_session"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("election_sessions.id", ondelete="CASCADE"), nullable=False
    )
    has_voted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    voted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="voter_statuses")
    session: Mapped["ElectionSession"] = relationship(back_populates="voter_statuses")
