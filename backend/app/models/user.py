from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AccessMode, sqlalchemy_enum
from app.models.mixins import IdMixin, TimestampMixin


class User(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    nim: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    nama: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    kelas: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mode_akses: Mapped[AccessMode] = mapped_column(
        sqlalchemy_enum(AccessMode, name="access_mode"), nullable=False, default=AccessMode.MANDIRI
    )
    face_enrolled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_voted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_dpt_member: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    face_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    face_profiles: Mapped[list["FaceProfile"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    voter_statuses: Mapped[list["VoterStatus"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    verification_logs: Mapped[list["FaceVerificationLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    assisted_sessions: Mapped[list["AssistedSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
