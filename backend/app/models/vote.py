from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Vote(Base, IdMixin, TimestampMixin):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("vote_token", name="uq_vote_token"),
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("election_sessions.id", ondelete="CASCADE"), nullable=False
    )
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id", ondelete="CASCADE"), nullable=False)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False
    )
    vote_token: Mapped[str] = mapped_column(String(64), nullable=False)

    session: Mapped["ElectionSession"] = relationship(back_populates="votes")
    position: Mapped["Position"] = relationship(back_populates="votes")
    candidate: Mapped["Candidate"] = relationship(back_populates="votes")
