from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.enums import VerificationResult


class FaceEnrollRequest(BaseModel):
    nim: str = Field(min_length=5, max_length=20)
    image_base64: str = Field(min_length=1)


class FaceEnrollResponse(BaseModel):
    success: bool
    face_enrolled: bool
    quality_score: int | None = None
    message: str


class FaceVerifyRequest(BaseModel):
    nim: str = Field(min_length=5, max_length=20)
    image_base64: str = Field(min_length=1)
    kiosk_device_id: str | None = None


class FaceVerifyResponse(BaseModel):
    verified: bool
    result: VerificationResult
    similarity_score: float | None = None
    liveness_score: float | None = None
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

