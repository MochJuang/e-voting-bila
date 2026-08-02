from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc

from app.api.deps import DbSession, get_current_user
from app.models import ElectionSession, Position
from app.schemas import BallotResponse, ElectionSessionResponse
from app.services.mock_helpers import default_session_response

router = APIRouter()


def _position_to_response(position: Position):
    return {
        "id": position.id,
        "session_id": position.session_id,
        "name": position.name,
        "is_required": position.is_required,
        "candidates": [
            {
                "id": candidate.id,
                "name": candidate.name,
                "number": candidate.number,
                "vision": candidate.vision,
                "photo_path": candidate.photo_path,
                "photo_base64": candidate.photo_base64,
                "color": candidate.color,
            }
            for candidate in position.candidates
        ],
    }


def _session_to_response(session: ElectionSession) -> ElectionSessionResponse:
    return ElectionSessionResponse(
        id=session.id,
        name=session.name,
        status=session.status,
        registration_open_at=session.registration_open_at,
        registration_close_at=session.registration_close_at,
        voting_open_at=session.voting_open_at,
        voting_close_at=session.voting_close_at,
        description=session.description,
        positions=[_position_to_response(position) for position in session.positions],
    )


@router.get("/active", response_model=ElectionSessionResponse)
def get_active_session(db: DbSession):
    session = (
        db.query(ElectionSession)
        .order_by(desc(ElectionSession.created_at))
        .first()
    )
    if not session:
        return default_session_response()
    return _session_to_response(session)


@router.get("/ballot", response_model=BallotResponse)
def get_ballot(db: DbSession, current_user=Depends(get_current_user)):
    session = (
        db.query(ElectionSession)
        .order_by(desc(ElectionSession.created_at))
        .first()
    )
    if not session:
        return BallotResponse(session=default_session_response())
    return BallotResponse(session=_session_to_response(session))
