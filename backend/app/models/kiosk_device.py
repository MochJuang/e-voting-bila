from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class KioskDevice(Base, IdMixin, TimestampMixin):
    __tablename__ = "kiosk_devices"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    device_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)

    assisted_sessions: Mapped[list["AssistedSession"]] = relationship(
        back_populates="kiosk_device", cascade="all, delete-orphan"
    )

