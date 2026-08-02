from sqlalchemy import JSON, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class FaceProfile(Base, IdMixin, TimestampMixin):
    __tablename__ = "face_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    # Blob terpaket (format .npy) — dipakai untuk pencocokan (best_similarity), sumber kebenaran.
    embedding: Mapped[bytes] = mapped_column(LargeBinary(length=65535), nullable=False)
    # Representasi yang sama persis, tapi sebagai array angka biasa (bukan blob biner) agar
    # mudah dibaca/diinspeksi langsung dari database. list[list[float]] — 5 baris (pose) x 512 kolom.
    embedding_vector: Mapped[list | None] = mapped_column(JSON, nullable=True)
    embedding_version: Mapped[str] = mapped_column(String(50), nullable=False, default="insightface-v1")
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Foto referensi (pose tengah) hasil registrasi, disimpan sebagai data URL base64
    # agar dapat ditampilkan kembali di dashboard mahasiswa maupun panel admin.
    # MEDIUMTEXT di MySQL (base64 JPEG bisa > 64KB); TEXT generik untuk dialek lain (mis. SQLite saat testing).
    photo_base64: Mapped[str | None] = mapped_column(Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=True)
    quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="face_profiles")

