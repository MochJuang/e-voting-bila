from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.enums import SessionStatus


class CandidateResponse(ORMModel):
    id: int
    name: str
    number: int
    vision: str | None = None
    photo_path: str | None = None
    photo_base64: str | None = None
    color: str | None = None


class PositionResponse(ORMModel):
    id: int
    session_id: int
    name: str
    is_required: bool
    candidates: list[CandidateResponse] = Field(default_factory=list)


class ElectionSessionResponse(ORMModel):
    id: int
    name: str
    status: SessionStatus
    registration_open_at: datetime | None = None
    registration_close_at: datetime | None = None
    voting_open_at: datetime | None = None
    voting_close_at: datetime | None = None
    description: str | None = None
    positions: list[PositionResponse] = Field(default_factory=list)


class BallotResponse(BaseModel):
    session: ElectionSessionResponse


class VoteSelectionItem(BaseModel):
    position_id: int
    candidate_id: int


class VoteSubmitRequest(BaseModel):
    session_id: int
    nim: str = Field(min_length=5, max_length=20)
    verification_token: str = Field(min_length=1)
    selections: list[VoteSelectionItem]


class VoteSubmitResponse(BaseModel):
    success: bool
    vote_reference_code: str
    message: str


class VotingConfirmationResponse(BaseModel):
    success: bool
    reference_code: str
    has_voted: bool
