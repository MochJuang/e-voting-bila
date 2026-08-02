from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Candidate(Base, IdMixin, TimestampMixin):
    __tablename__ = "candidates"
    __table_args__ = (
        UniqueConstraint("position_id", "number", name="uq_candidates_position_number"),
    )

    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    number: Mapped[int] = mapped_column(nullable=False)
    vision: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Foto kandidat sebagai data URL base64 (dikompres), ditampilkan di panel admin & surat suara.
    photo_base64: Mapped[str | None] = mapped_column(Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)

    position: Mapped["Position"] = relationship(back_populates="candidates")
    votes: Mapped[list["Vote"]] = relationship(back_populates="candidate")

