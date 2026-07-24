from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class AdminAccount(Base, IdMixin, TimestampMixin):
    __tablename__ = "admin_accounts"

    username: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="admin")

    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="admin")
    assisted_sessions: Mapped[list["AssistedSession"]] = relationship(
        back_populates="admin", cascade="all, delete-orphan"
    )
