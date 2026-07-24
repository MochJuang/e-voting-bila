from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc

from app.api.deps import DbSession, get_current_user
from app.core.security import validate_token_claims
from app.models import Candidate, ElectionSession, Position, VoterStatus, Vote
from app.models.enums import SessionStatus
from app.schemas import VoteSubmitRequest, VoteSubmitResponse, VotingConfirmationResponse
from app.services.mock_helpers import ensure_default_election_data

router = APIRouter()


def _get_active_session(db: DbSession) -> ElectionSession:
    session = db.query(ElectionSession).order_by(desc(ElectionSession.created_at)).first()
    if session:
        return session
    return ensure_default_election_data(db)


@router.post("/submit", response_model=VoteSubmitResponse)
def submit_vote(payload: VoteSubmitRequest, db: DbSession, current_user=Depends(get_current_user)):
    if current_user.nim != payload.nim:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak bisa submit untuk NIM lain")

    try:
        validate_token_claims(
            payload.verification_token,
            expected_subject=current_user.nim,
            required_claims={"purpose": "face_verified"},
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    session = _get_active_session(db)
    if session.status not in {SessionStatus.VOTING_OPEN, SessionStatus.CLOSED}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sesi pemilihan belum dibuka")

    voter_status = (
        db.query(VoterStatus)
        .filter(VoterStatus.user_id == current_user.id, VoterStatus.session_id == session.id)
        .first()
    )
    if voter_status and voter_status.has_voted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mahasiswa sudah memilih")

    positions = list(session.positions)
    if len(payload.selections) != len(positions):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Semua jabatan wajib diisi")

    selections_by_position = {item.position_id: item.candidate_id for item in payload.selections}
    for position in positions:
        candidate_id = selections_by_position.get(position.id)
        if candidate_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Jabatan {position.name} belum dipilih")
        candidate = (
            db.query(Candidate)
            .filter(Candidate.id == candidate_id, Candidate.position_id == position.id)
            .first()
        )
        if not candidate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kandidat tidak valid")

        db.add(
            Vote(
                session_id=session.id,
                position_id=position.id,
                candidate_id=candidate.id,
                vote_token=uuid4().hex,
            )
        )

    if not voter_status:
        voter_status = VoterStatus(user_id=current_user.id, session_id=session.id, has_voted=True)
        db.add(voter_status)
    else:
        voter_status.has_voted = True
    current_user.has_voted = True
    db.commit()

    return VoteSubmitResponse(
        success=True,
        vote_reference_code=f"VT-{uuid4().hex[:8].upper()}",
        message="Suara berhasil disimpan.",
    )


@router.get("/confirmation", response_model=VotingConfirmationResponse)
def vote_confirmation(db: DbSession, current_user=Depends(get_current_user)):
    session = _get_active_session(db)
    voter_status = (
        db.query(VoterStatus)
        .filter(VoterStatus.user_id == current_user.id, VoterStatus.session_id == session.id)
        .first()
    )
    return VotingConfirmationResponse(
        success=bool(current_user.has_voted or (voter_status and voter_status.has_voted)),
        reference_code=f"VT-{current_user.nim[-4:]}",
        has_voted=bool(voter_status and voter_status.has_voted),
    )
