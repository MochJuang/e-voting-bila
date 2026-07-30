from __future__ import annotations

from collections import defaultdict

from app.core.security import hash_password
from app.models import AdminAccount, Candidate, ElectionSession, FaceProfile, FaceVerificationLog, Position, User, Vote
from app.schemas.admin import AdminDashboardResponse, AdminDashboardStats, PositionResult, RecapResponse, ResultSummary
from app.schemas.election import CandidateResponse, ElectionSessionResponse, PositionResponse
from app.schemas.face import FacePhotoResponse
from app.services.mock_data import DEFAULT_ADMINS, DEFAULT_POSITIONS, DEFAULT_SESSION, DEFAULT_VOTERS


def find_default_voter(nim: str):
    return next((v for v in DEFAULT_VOTERS if v.nim == nim), None)


def find_default_admin(username: str):
    return next((a for a in DEFAULT_ADMINS if a.username == username), None)


def default_session_response() -> ElectionSessionResponse:
    positions = [
        PositionResponse(
            id=index + 1,
            session_id=DEFAULT_SESSION["id"],
            name=position.nama,
            is_required=True,
            candidates=[
                CandidateResponse(
                    id=candidate.id,
                    name=candidate.nama,
                    number=candidate.nomor,
                    vision=candidate.visi,
                    photo_path=None,
                    color=candidate.warna,
                )
                for candidate in position.kandidat
            ],
        )
        for index, position in enumerate(DEFAULT_POSITIONS)
    ]
    return ElectionSessionResponse(
        id=DEFAULT_SESSION["id"],
        name=DEFAULT_SESSION["name"],
        status=DEFAULT_SESSION["status"],
        registration_open_at=DEFAULT_SESSION["registration_open_at"],
        registration_close_at=DEFAULT_SESSION["registration_close_at"],
        voting_open_at=DEFAULT_SESSION["voting_open_at"],
        voting_close_at=DEFAULT_SESSION["voting_close_at"],
        description=DEFAULT_SESSION["description"],
        positions=positions,
    )


def default_dashboard_stats(total_dpt: int | None = None, sudah_memilih: int | None = None) -> AdminDashboardResponse:
    total = total_dpt if total_dpt is not None else len(DEFAULT_VOTERS)
    voted = sudah_memilih if sudah_memilih is not None else sum(1 for v in DEFAULT_VOTERS if v.has_voted)
    stats = AdminDashboardStats(
        total_dpt=total,
        sudah_memilih=voted,
        belum_memilih=max(total - voted, 0),
        mode_mandiri=sum(1 for v in DEFAULT_VOTERS if v.mode_akses.value == "mandiri"),
        mode_admin_assisted=sum(1 for v in DEFAULT_VOTERS if v.mode_akses.value == "admin_assisted"),
        session_status=DEFAULT_SESSION["status"],
        session_name=DEFAULT_SESSION["name"],
    )
    return AdminDashboardResponse(stats=stats)


def summarize_votes_from_db(session_id: int, votes: list[Vote], candidates: list[Candidate], positions: list[Position]) -> RecapResponse:
    position_index = {position.id: position for position in positions}

    counts: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for vote in votes:
        counts[vote.position_id][vote.candidate_id] += 1

    recap_positions: list[PositionResult] = []
    for position in positions:
        position_votes = counts.get(position.id, {})
        total_votes = sum(position_votes.values()) or 1
        result_items: list[ResultSummary] = []
        for candidate in position_index[position.id].candidates:
            vote_count = position_votes.get(candidate.id, 0)
            result_items.append(
                ResultSummary(
                    candidate_id=candidate.id,
                    candidate_name=candidate.name,
                    number=candidate.number,
                    votes=vote_count,
                    percentage=round((vote_count / total_votes) * 100, 2),
                )
            )
        recap_positions.append(
            PositionResult(
                position_id=position.id,
                position_name=position.name,
                results=result_items,
            )
        )

    return RecapResponse(
        session_id=session_id,
        session_name="Rekapitulasi Sesi Aktif",
        total_dpt=0,
        total_voted=0,
        positions=recap_positions,
    )


def ensure_default_election_data(db):
    session = db.query(ElectionSession).filter(ElectionSession.name == DEFAULT_SESSION["name"]).first()
    if not session:
        session = ElectionSession(
            name=DEFAULT_SESSION["name"],
            status=DEFAULT_SESSION["status"],
            description=DEFAULT_SESSION["description"],
        )
        db.add(session)
        db.flush()

    positions_by_name = {position.name: position for position in session.positions}

    for position in DEFAULT_POSITIONS:
        position_row = positions_by_name.get(position.nama)
        if not position_row:
            position_row = Position(
                session_id=session.id,
                name=position.nama,
                is_required=True,
            )
            db.add(position_row)
            db.flush()
            positions_by_name[position.nama] = position_row

        existing_numbers = {candidate.number for candidate in position_row.candidates}
        for candidate in position.kandidat:
            if candidate.nomor in existing_numbers:
                continue
            db.add(
                Candidate(
                    position_id=position_row.id,
                    name=candidate.nama,
                    number=candidate.nomor,
                    vision=candidate.visi,
                    color=candidate.warna,
                    photo_path=None,
                )
            )

    db.commit()
    db.refresh(session)
    return session


def ensure_default_voters(db):
    existing_by_nim = {user.nim for user in db.query(User).all()}
    created = False

    for voter in DEFAULT_VOTERS:
        if voter.nim in existing_by_nim:
            continue
        db.add(
            User(
                nim=voter.nim,
                nama=voter.nama,
                kelas=voter.kelas,
                mode_akses=voter.mode_akses,
                password_hash=hash_password("password"),
                face_enrolled=voter.face_enrolled,
                has_voted=voter.has_voted,
                is_dpt_member=True,
            )
        )
        created = True

    if created:
        db.commit()


def ensure_default_admins(db):
    existing_by_username = {admin.username for admin in db.query(AdminAccount).all()}
    created = False

    for admin in DEFAULT_ADMINS:
        if admin.username in existing_by_username:
            continue
        db.add(
            AdminAccount(
                username=admin.username,
                password_hash=hash_password(admin.password),
                role=admin.role,
            )
        )
        created = True

    if created:
        db.commit()


def build_face_photo_response(db, user: User) -> FacePhotoResponse:
    """Foto wajah hasil registrasi + cuplikan verifikasi terakhir (saat memilih)."""
    profile = db.query(FaceProfile).filter(FaceProfile.user_id == user.id).first()
    last_log = (
        db.query(FaceVerificationLog)
        .filter(FaceVerificationLog.user_id == user.id, FaceVerificationLog.snapshot_base64.isnot(None))
        .order_by(FaceVerificationLog.created_at.desc())
        .first()
    )
    return FacePhotoResponse(
        nim=user.nim,
        enrolled_photo=profile.photo_base64 if profile else None,
        enrolled_at=profile.updated_at if profile else None,
        last_verification_photo=last_log.snapshot_base64 if last_log else None,
        last_verification_at=last_log.created_at if last_log else None,
        last_verification_result=last_log.result if last_log else None,
    )
