from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.enums import FacePose, LivenessChallenge, VerificationResult, VerifyStage


# --------------------------------------------------------------------------- #
# Enrollment (multi-pose)
# --------------------------------------------------------------------------- #
class FaceEnrollFrame(BaseModel):
    pose: FacePose
    image_base64: str = Field(min_length=1)


class FaceEnrollRequest(BaseModel):
    nim: str = Field(min_length=5, max_length=20)
    frames: list[FaceEnrollFrame] = Field(min_length=1)


class PoseEnrollResultResponse(BaseModel):
    pose: FacePose
    accepted: bool
    quality_score: int
    message: str


class FaceEnrollResponse(BaseModel):
    success: bool
    face_enrolled: bool
    quality_score: int | None = None
    poses: list[PoseEnrollResultResponse] = Field(default_factory=list)
    message: str


# --------------------------------------------------------------------------- #
# Verification (realtime: match -> liveness)
# --------------------------------------------------------------------------- #
class FaceVerifyRequest(BaseModel):
    nim: str = Field(min_length=5, max_length=20)
    image_base64: str = Field(min_length=1)
    stage: VerifyStage = VerifyStage.MATCH
    challenge: LivenessChallenge | None = None
    timed_out: bool = False
    kiosk_device_id: str | None = None


class FaceVerifyResponse(BaseModel):
    stage: VerifyStage
    verified: bool = False
    matched: bool = False
    result: VerificationResult
    similarity_score: float | None = None
    liveness_score: float | None = None
    challenge: LivenessChallenge | None = None
    liveness_passed: bool = False
    retry_count: int = 0
    lock_applied: bool = False
    verification_token: str | None = None
    message: str


class FaceLogResponse(ORMModel):
    id: int
    user_id: int
    result: VerificationResult
    similarity_score: float | None = None
    liveness_score: float | None = None
    reason: str | None = None
    device_info: str | None = None


# --------------------------------------------------------------------------- #
# Tampilan foto: wajah hasil registrasi & cuplikan saat proses memilih
# --------------------------------------------------------------------------- #
class FacePhotoResponse(BaseModel):
    nim: str
    enrolled_photo: str | None = None
    enrolled_at: datetime | None = None
    last_verification_photo: str | None = None
    last_verification_at: datetime | None = None
    last_verification_result: VerificationResult | None = None
