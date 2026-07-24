from pydantic import BaseModel

from app.schemas.common import ORMModel
from app.schemas.enums import AccessMode


class VoterBase(ORMModel):
    id: int
    nim: str
    nama: str
    kelas: str | None = None
    mode_akses: AccessMode
    face_enrolled: bool
    has_voted: bool
    is_locked: bool
    is_dpt_member: bool


class VoterDetailResponse(VoterBase):
    email: str | None = None
    face_note: str | None = None


class VoterStatusResponse(BaseModel):
    nim: str
    nama: str
    face_enrolled: bool
    has_voted: bool
    mode_akses: AccessMode
    is_locked: bool
    can_vote: bool
    next_step: str


class VoterImportResponse(BaseModel):
    imported: int
    skipped: int
    message: str

