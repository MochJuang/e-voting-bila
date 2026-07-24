from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AssistedSessionResult, sqlalchemy_enum
from app.models.mixins import IdMixin, TimestampMixin


class AssistedSession(Base, IdMixin, TimestampMixin):
    __tablename__ = "assisted_sessions"

    admin_id: Mapped[int] = mapped_column(
        ForeignKey("admin_accounts.id", ondelete="CASCADE"), nullable=False
    )
    kiosk_device_id: Mapped[int] = mapped_column(
        ForeignKey("kiosk_devices.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[AssistedSessionResult | None] = mapped_column(
        sqlalchemy_enum(AssistedSessionResult, name="assisted_session_result"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    admin: Mapped["AdminAccount"] = relationship(back_populates="assisted_sessions")
    kiosk_device: Mapped["KioskDevice"] = relationship(back_populates="assisted_sessions")
    user: Mapped["User"] = relationship(back_populates="assisted_sessions")
