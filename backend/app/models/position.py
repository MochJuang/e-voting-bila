from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Position(Base, IdMixin, TimestampMixin):
    __tablename__ = "positions"

    session_id: Mapped[int] = mapped_column(ForeignKey("election_sessions.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    session: Mapped["ElectionSession"] = relationship(back_populates="positions")
    candidates: Mapped[list["Candidate"]] = relationship(
        back_populates="position", cascade="all, delete-orphan"
    )
    votes: Mapped[list["Vote"]] = relationship(back_populates="position", cascade="all, delete-orphan")
