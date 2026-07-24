from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc

from app.api.deps import DbSession, get_current_user
from app.models import ElectionSession, User, VoterStatus
from app.schemas import VoterDetailResponse, VoterStatusResponse
from app.services.mock_helpers import ensure_default_election_data, find_default_voter

router = APIRouter()


def _user_to_voter_detail(user: User) -> VoterDetailResponse:
    return VoterDetailResponse.model_validate(user)


def _active_session(db: DbSession) -> ElectionSession:
    ensure_default_election_data(db)
    session = db.query(ElectionSession).order_by(desc(ElectionSession.created_at)).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesi pemilihan tidak ditemukan")
    return session


@router.get("/me", response_model=VoterDetailResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return _user_to_voter_detail(current_user)


@router.get("/me/status", response_model=VoterStatusResponse)
def get_my_status(db: DbSession, current_user: User = Depends(get_current_user)):
    session = _active_session(db)
    voter_status = (
        db.query(VoterStatus)
        .filter(VoterStatus.user_id == current_user.id, VoterStatus.session_id == session.id)
        .first()
    )

    has_voted = bool(voter_status and voter_status.has_voted)
    can_vote = current_user.face_enrolled and not has_voted and not current_user.is_locked
    if current_user.is_locked:
        next_step = "hubungi panitia"
    elif not current_user.face_enrolled:
        next_step = "registrasi wajah"
    elif has_voted:
        next_step = "sudah memilih"
    else:
        next_step = "verifikasi wajah"

    default_voter = find_default_voter(current_user.nim)
    return VoterStatusResponse(
        nim=current_user.nim,
        nama=current_user.nama,
        face_enrolled=current_user.face_enrolled if current_user else bool(default_voter and default_voter.face_enrolled),
        has_voted=has_voted,
        mode_akses=current_user.mode_akses,
        is_locked=current_user.is_locked,
        can_vote=can_vote,
        next_step=next_step,
    )


@router.get("/{nim}", response_model=VoterDetailResponse)
def get_voter_by_nim(nim: str, db: DbSession):
    voter = db.query(User).filter(User.nim == nim).first()
    if not voter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahasiswa tidak ditemukan")
    return _user_to_voter_detail(voter)
