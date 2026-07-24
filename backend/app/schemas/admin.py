from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.enums import AssistedSessionResult, AccessMode, SessionStatus


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=128)


class AdminUserResponse(ORMModel):
    id: int
    username: str
    role: str


class AdminDashboardStats(BaseModel):
    total_dpt: int
    sudah_memilih: int
    belum_memilih: int
    mode_mandiri: int
    mode_admin_assisted: int
    session_status: SessionStatus
    session_name: str | None = None


class AdminDashboardResponse(BaseModel):
    stats: AdminDashboardStats


class CandidateForm(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    number: int = Field(ge=1)
    vision: str | None = None
    photo_path: str | None = None
    color: str | None = None


class PositionForm(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    is_required: bool = True


class VoterForm(BaseModel):
    nim: str = Field(min_length=5, max_length=20)
    nama: str = Field(min_length=1, max_length=150)
    kelas: str | None = None
    mode_akses: AccessMode = AccessMode.MANDIRI
    email: str | None = None


class KioskDeviceForm(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    device_id: str = Field(min_length=1, max_length=100)
    ip_address: str | None = None
    is_active: bool = True
    location: str | None = None


class AssistedSessionResponse(ORMModel):
    id: int
    admin_id: int
    kiosk_device_id: int
    user_id: int
    started_at: datetime | None = None
    ended_at: datetime | None = None
    result: AssistedSessionResult | None = None
    notes: str | None = None


class ResultSummary(BaseModel):
    candidate_id: int
    candidate_name: str
    number: int
    votes: int
    percentage: float


class PositionResult(BaseModel):
    position_id: int
    position_name: str
    results: list[ResultSummary]


class RecapResponse(BaseModel):
    session_id: int
    session_name: str
    total_dpt: int
    total_voted: int
    positions: list[PositionResult]

