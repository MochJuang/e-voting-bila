from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import SessionStatus, sqlalchemy_enum
from app.models.mixins import IdMixin, TimestampMixin


class ElectionSession(Base, IdMixin, TimestampMixin):
    __tablename__ = "election_sessions"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        sqlalchemy_enum(SessionStatus, name="session_status"), nullable=False, default=SessionStatus.DRAFT
    )
    registration_open_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    registration_close_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    voting_open_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    voting_close_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    positions: Mapped[list["Position"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    voter_statuses: Mapped[list["VoterStatus"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    votes: Mapped[list["Vote"]] = relationship(back_populates="session", cascade="all, delete-orphan")
