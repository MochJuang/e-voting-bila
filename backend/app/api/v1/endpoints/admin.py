from __future__ import annotations

from io import BytesIO
import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.api.deps import DbSession, get_current_admin
from app.core.security import create_access_token, hash_password, verify_password
from app.models import AdminAccount, Candidate, ElectionSession, KioskDevice, Position, User, Vote, VoterStatus
from app.models.enums import AccessMode
from app.schemas import (
    AdminAccountCreate,
    AdminAccountUpdate,
    AdminDashboardResponse,
    AdminLoginRequest,
    AdminUserResponse,
    BulkVoterRequest,
    BulkVoterResponse,
    BulkVoterResultItem,
    CandidateForm,
    FacePhotoResponse,
    KioskDeviceForm,
    MessageResponse,
    PositionForm,
    PositionResponse,
    RecapResponse,
    TokenResponse,
    VoterDetailResponse,
    VoterForm,
)
from app.services.face_service import FaceServiceError, face_service
from app.services.mock_helpers import (
    build_face_photo_response,
    ensure_default_election_data,
    ensure_default_admins,
    ensure_default_voters,
)

router = APIRouter()


def _active_session(db: DbSession) -> ElectionSession:
    ensure_default_election_data(db)
    session = db.query(ElectionSession).order_by(desc(ElectionSession.created_at)).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesi pemilihan tidak ditemukan")
    return session


def _position_to_response(position: Position) -> PositionResponse:
    return PositionResponse(
        id=position.id,
        session_id=position.session_id,
        name=position.name,
        is_required=position.is_required,
        candidates=[
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
    )


def _compress_candidate_photo(photo_base64: str | None) -> str | None:
    """Kompres foto kandidat yang diunggah admin agar hemat penyimpanan."""
    if not photo_base64:
        return None
    try:
        image_bytes = face_service.decode_base64(photo_base64)
        return face_service.to_display_photo(image_bytes, max_side=460)
    except FaceServiceError:
        return photo_base64


def _voter_to_response(voter: User) -> VoterDetailResponse:
    return VoterDetailResponse.model_validate(voter)


def _candidate_to_dict(candidate: Candidate) -> dict:
    return {
        "id": candidate.id,
        "position_id": candidate.position_id,
        "name": candidate.name,
        "number": candidate.number,
        "vision": candidate.vision,
        "photo_path": candidate.photo_path,
        "photo_base64": candidate.photo_base64,
        "color": candidate.color,
    }


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    return cleaned or "rekapitulasi"


def _build_recap_data(db: DbSession) -> dict:
    session = _active_session(db)
    positions = list(session.positions)
    votes = db.query(Vote).filter(Vote.session_id == session.id).all()
    total_dpt = db.query(User).count()
    total_voted = db.query(VoterStatus).filter(VoterStatus.session_id == session.id, VoterStatus.has_voted.is_(True)).count()

    recap_positions = []
    for position in positions:
        candidate_results = []
        position_votes = [vote for vote in votes if vote.position_id == position.id]
        total_position_votes = len(position_votes) or 1
        for candidate in position.candidates:
            count = sum(1 for vote in position_votes if vote.candidate_id == candidate.id)
            candidate_results.append(
                {
                    "candidate_id": candidate.id,
                    "candidate_name": candidate.name,
                    "number": candidate.number,
                    "votes": count,
                    "percentage": round((count / total_position_votes) * 100, 2),
                }
            )
        recap_positions.append(
            {
                "position_id": position.id,
                "position_name": position.name,
                "results": candidate_results,
            }
        )

    return {
        "session_id": session.id,
        "session_name": session.name,
        "total_dpt": total_dpt,
        "total_voted": total_voted,
        "positions": recap_positions,
    }


@router.post("/auth/login", response_model=TokenResponse)
def admin_login(payload: AdminLoginRequest, db: DbSession):
    ensure_default_admins(db)
    admin = db.query(AdminAccount).filter(AdminAccount.username == payload.username).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin tidak ditemukan")
    elif not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password admin salah")

    token = create_access_token(admin.username, extra_claims={"role": "admin"})
    return TokenResponse(access_token=token)


@router.get("/dashboard", response_model=AdminDashboardResponse)
def read_dashboard(db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    ensure_default_voters(db)
    session = _active_session(db)
    total = db.query(User).count()
    mandiri = db.query(User).filter(User.mode_akses == AccessMode.MANDIRI).count()
    assisted = db.query(User).filter(User.mode_akses == AccessMode.ADMIN_ASSISTED).count()
    voted = (
        db.query(VoterStatus)
        .filter(VoterStatus.session_id == session.id, VoterStatus.has_voted.is_(True))
        .count()
    )
    return AdminDashboardResponse(
        stats={
            "total_dpt": total,
            "sudah_memilih": voted,
            "belum_memilih": max(total - voted, 0),
            "mode_mandiri": mandiri,
            "mode_admin_assisted": assisted,
            "session_status": session.status,
            "session_name": session.name,
        }
    )


@router.get("/voters", response_model=list[VoterDetailResponse])
def list_voters(db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    ensure_default_voters(db)
    voters = db.query(User).order_by(User.nim.asc()).all()
    return [_voter_to_response(voter) for voter in voters]


@router.get("/voters/{nim}/face-photo", response_model=FacePhotoResponse)
def get_voter_face_photo(nim: str, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    voter = db.query(User).filter(User.nim == nim).first()
    if not voter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahasiswa tidak ditemukan")
    return build_face_photo_response(db, voter)


@router.post("/voters", response_model=VoterDetailResponse)
def create_voter(payload: VoterForm, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    if db.query(User).filter(User.nim == payload.nim).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NIM sudah terdaftar")
    voter = User(
        nim=payload.nim,
        nama=payload.nama,
        kelas=payload.kelas,
        password_hash=hash_password(payload.password or "password"),
        email=payload.email,
        is_dpt_member=True,
        face_enrolled=False,
        has_voted=False,
    )
    voter.mode_akses = payload.mode_akses
    db.add(voter)
    db.commit()
    db.refresh(voter)
    return _voter_to_response(voter)


@router.post("/voters/bulk", response_model=BulkVoterResponse)
def bulk_create_voters(payload: BulkVoterRequest, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    """Buat banyak mahasiswa sekaligus. NIM yang sudah ada dilewati (skipped)."""
    existing = {nim for (nim,) in db.query(User.nim).all()}
    items: list[BulkVoterResultItem] = []
    created = 0
    seen: set[str] = set()

    for form in payload.voters:
        if form.nim in existing or form.nim in seen:
            items.append(BulkVoterResultItem(nim=form.nim, status="skipped", reason="NIM sudah terdaftar"))
            continue
        voter = User(
            nim=form.nim,
            nama=form.nama,
            kelas=form.kelas,
            password_hash=hash_password(form.password or "password"),
            email=form.email,
            is_dpt_member=True,
            face_enrolled=False,
            has_voted=False,
        )
        voter.mode_akses = form.mode_akses
        db.add(voter)
        seen.add(form.nim)
        created += 1
        items.append(BulkVoterResultItem(nim=form.nim, status="created"))

    db.commit()
    return BulkVoterResponse(created=created, skipped=len(items) - created, items=items)


@router.patch("/voters/{nim}", response_model=VoterDetailResponse)
def update_voter(nim: str, payload: VoterForm, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    voter = db.query(User).filter(User.nim == nim).first()
    if not voter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahasiswa tidak ditemukan")
    voter.nama = payload.nama
    voter.kelas = payload.kelas
    voter.email = payload.email
    voter.mode_akses = payload.mode_akses
    # Reset password bila diisi.
    if payload.password:
        voter.password_hash = hash_password(payload.password)
        voter.is_locked = False
    db.commit()
    db.refresh(voter)
    return _voter_to_response(voter)


@router.delete("/voters/{nim}", response_model=MessageResponse)
def delete_voter(nim: str, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    voter = db.query(User).filter(User.nim == nim).first()
    if not voter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahasiswa tidak ditemukan")
    db.delete(voter)
    db.commit()
    return MessageResponse(message="Mahasiswa berhasil dihapus.")


# --------------------------------------------------------------------------- #
# Manajemen akun admin/panitia (edit data login + reset password)
# --------------------------------------------------------------------------- #
def _admin_to_response(account: AdminAccount) -> AdminUserResponse:
    return AdminUserResponse(id=account.id, username=account.username, role=account.role)


@router.get("/accounts", response_model=list[AdminUserResponse])
def list_admin_accounts(db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    ensure_default_admins(db)
    return [_admin_to_response(a) for a in db.query(AdminAccount).order_by(AdminAccount.id).all()]


@router.post("/accounts", response_model=AdminUserResponse)
def create_admin_account(payload: AdminAccountCreate, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    if db.query(AdminAccount).filter(AdminAccount.username == payload.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username sudah digunakan")
    account = AdminAccount(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role or "admin",
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return _admin_to_response(account)


@router.patch("/accounts/{account_id}", response_model=AdminUserResponse)
def update_admin_account(
    account_id: int, payload: AdminAccountUpdate, db: DbSession, admin: AdminAccount = Depends(get_current_admin)
):
    account = db.query(AdminAccount).filter(AdminAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Akun admin tidak ditemukan")
    if payload.username and payload.username != account.username:
        if db.query(AdminAccount).filter(AdminAccount.username == payload.username).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username sudah digunakan")
        account.username = payload.username
    if payload.role:
        account.role = payload.role
    if payload.password:
        account.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(account)
    return _admin_to_response(account)


@router.delete("/accounts/{account_id}", response_model=MessageResponse)
def delete_admin_account(account_id: int, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    account = db.query(AdminAccount).filter(AdminAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Akun admin tidak ditemukan")
    if db.query(AdminAccount).count() <= 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimal harus ada satu akun admin")
    db.delete(account)
    db.commit()
    return MessageResponse(message="Akun admin berhasil dihapus.")


@router.get("/positions", response_model=list[PositionResponse])
def list_positions(db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    session = _active_session(db)
    return [_position_to_response(position) for position in session.positions]


@router.post("/positions", response_model=PositionResponse)
def create_position(payload: PositionForm, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    session = _active_session(db)
    position = Position(session_id=session.id, name=payload.name, is_required=payload.is_required)
    db.add(position)
    db.commit()
    db.refresh(position)
    return _position_to_response(position)


@router.patch("/positions/{position_id}", response_model=PositionResponse)
def update_position(position_id: int, payload: PositionForm, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jabatan tidak ditemukan")
    position.name = payload.name
    position.is_required = payload.is_required
    db.commit()
    db.refresh(position)
    return _position_to_response(position)


@router.delete("/positions/{position_id}", response_model=MessageResponse)
def delete_position(position_id: int, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jabatan tidak ditemukan")
    db.delete(position)
    db.commit()
    return MessageResponse(message="Jabatan berhasil dihapus.")


@router.get("/positions/{position_id}/candidates", response_model=list[dict])
def list_candidates(position_id: int, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jabatan tidak ditemukan")
    return [
        {
            "id": candidate.id,
            "position_id": candidate.position_id,
            "name": candidate.name,
            "number": candidate.number,
            "vision": candidate.vision,
            "photo_path": candidate.photo_path,
            "color": candidate.color,
        }
        for candidate in position.candidates
    ]


@router.post("/positions/{position_id}/candidates", response_model=dict)
def create_candidate(position_id: int, payload: CandidateForm, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jabatan tidak ditemukan")

    duplicate = (
        db.query(Candidate)
        .filter(Candidate.position_id == position_id, Candidate.number == payload.number)
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nomor kandidat {payload.number} sudah dipakai pada jabatan ini",
        )

    candidate = Candidate(
        position_id=position.id,
        name=payload.name,
        number=payload.number,
        vision=payload.vision,
        photo_path=payload.photo_path,
        photo_base64=_compress_candidate_photo(payload.photo_base64),
        color=payload.color,
    )
    db.add(candidate)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nomor kandidat {payload.number} sudah dipakai pada jabatan ini",
        ) from exc
    db.refresh(candidate)
    return _candidate_to_dict(candidate)


@router.patch("/positions/{position_id}/candidates/{candidate_id}", response_model=dict)
def update_candidate(
    position_id: int,
    candidate_id: int,
    payload: CandidateForm,
    db: DbSession,
    admin: AdminAccount = Depends(get_current_admin),
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.position_id == position_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kandidat tidak ditemukan")

    duplicate = (
        db.query(Candidate)
        .filter(
            Candidate.position_id == position_id,
            Candidate.number == payload.number,
            Candidate.id != candidate_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nomor kandidat {payload.number} sudah dipakai pada jabatan ini",
        )

    candidate.name = payload.name
    candidate.number = payload.number
    candidate.vision = payload.vision
    candidate.photo_path = payload.photo_path
    if payload.photo_base64:
        candidate.photo_base64 = _compress_candidate_photo(payload.photo_base64)
    candidate.color = payload.color
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nomor kandidat {payload.number} sudah dipakai pada jabatan ini",
        ) from exc
    db.refresh(candidate)
    return _candidate_to_dict(candidate)


@router.delete("/positions/{position_id}/candidates/{candidate_id}", response_model=MessageResponse)
def delete_candidate(
    position_id: int,
    candidate_id: int,
    db: DbSession,
    admin: AdminAccount = Depends(get_current_admin),
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id, Candidate.position_id == position_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kandidat tidak ditemukan")
    db.delete(candidate)
    db.commit()
    return MessageResponse(message="Kandidat berhasil dihapus.")


@router.get("/kiosks", response_model=list[dict])
def list_kiosks(db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    kiosks = db.query(KioskDevice).order_by(KioskDevice.id.asc()).all()
    return [
        {
            "id": kiosk.id,
            "name": kiosk.name,
            "device_id": kiosk.device_id,
            "ip_address": kiosk.ip_address,
            "is_active": kiosk.is_active,
            "location": kiosk.location,
        }
        for kiosk in kiosks
    ]


@router.post("/kiosks", response_model=dict)
def create_kiosk(payload: KioskDeviceForm, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    kiosk = KioskDevice(
        name=payload.name,
        device_id=payload.device_id,
        ip_address=payload.ip_address,
        is_active=payload.is_active,
        location=payload.location,
    )
    db.add(kiosk)
    db.commit()
    db.refresh(kiosk)
    return {
        "id": kiosk.id,
        "name": kiosk.name,
        "device_id": kiosk.device_id,
        "ip_address": kiosk.ip_address,
        "is_active": kiosk.is_active,
        "location": kiosk.location,
    }


@router.patch("/kiosks/{kiosk_id}", response_model=dict)
def update_kiosk(kiosk_id: int, payload: KioskDeviceForm, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    kiosk = db.query(KioskDevice).filter(KioskDevice.id == kiosk_id).first()
    if not kiosk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kiosk tidak ditemukan")
    kiosk.name = payload.name
    kiosk.device_id = payload.device_id
    kiosk.ip_address = payload.ip_address
    kiosk.is_active = payload.is_active
    kiosk.location = payload.location
    db.commit()
    db.refresh(kiosk)
    return {
        "id": kiosk.id,
        "name": kiosk.name,
        "device_id": kiosk.device_id,
        "ip_address": kiosk.ip_address,
        "is_active": kiosk.is_active,
        "location": kiosk.location,
    }


@router.delete("/kiosks/{kiosk_id}", response_model=MessageResponse)
def delete_kiosk(kiosk_id: int, db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    kiosk = db.query(KioskDevice).filter(KioskDevice.id == kiosk_id).first()
    if not kiosk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kiosk tidak ditemukan")
    db.delete(kiosk)
    db.commit()
    return MessageResponse(message="Kiosk berhasil dihapus.")


@router.get("/results", response_model=RecapResponse)
def read_results(db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    return RecapResponse(**_build_recap_data(db))


@router.get("/results/export/pdf")
def export_pdf(db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    recap = _build_recap_data(db)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"Rekapitulasi {recap['session_name']}", styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            f"Total DPT: {recap['total_dpt']} | Sudah memilih: {recap['total_voted']}",
            styles["BodyText"],
        ),
        Spacer(1, 12),
    ]

    for position in recap["positions"]:
        story.append(Paragraph(position["position_name"], styles["Heading2"]))
        table_data = [["No", "Kandidat", "Suara", "Persentase"]]
        for result in position["results"]:
            table_data.append(
                [
                    str(result["number"]),
                    result["candidate_name"],
                    str(result["votes"]),
                    f"{result['percentage']:.2f}%",
                ]
            )
        table = Table(table_data, colWidths=[50, 280, 80, 100])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#eef2ff")]),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.extend([table, Spacer(1, 16)])

    doc.build(story)
    buffer.seek(0)
    filename = f"{_safe_filename(recap['session_name'])}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/results/export/excel")
def export_excel(db: DbSession, admin: AdminAccount = Depends(get_current_admin)):
    recap = _build_recap_data(db)
    buffer = BytesIO()
    workbook = xlsxwriter.Workbook(buffer, {"in_memory": True})
    title_fmt = workbook.add_format({"bold": True, "font_size": 14})
    header_fmt = workbook.add_format({"bold": True, "bg_color": "#1f2937", "font_color": "white", "border": 1})
    text_fmt = workbook.add_format({"border": 1})
    int_fmt = workbook.add_format({"border": 1, "num_format": "0"})
    pct_fmt = workbook.add_format({"border": 1, "num_format": "0.00%"})

    summary = workbook.add_worksheet("Ringkasan")
    summary.write(0, 0, f"Rekapitulasi {recap['session_name']}", title_fmt)
    summary.write(2, 0, "Total DPT", header_fmt)
    summary.write(2, 1, recap["total_dpt"], int_fmt)
    summary.write(3, 0, "Sudah memilih", header_fmt)
    summary.write(3, 1, recap["total_voted"], int_fmt)

    row = 5
    for position in recap["positions"]:
        summary.write(row, 0, position["position_name"], header_fmt)
        row += 1
        summary.write_row(row, 0, ["No", "Kandidat", "Suara", "Persentase"], header_fmt)
        row += 1
        for result in position["results"]:
            summary.write(row, 0, result["number"], int_fmt)
            summary.write(row, 1, result["candidate_name"], text_fmt)
            summary.write(row, 2, result["votes"], int_fmt)
            summary.write(row, 3, result["percentage"] / 100, pct_fmt)
            row += 1
        row += 2

    for position in recap["positions"]:
        sheet_name = _safe_filename(position["position_name"])[:31]
        sheet = workbook.add_worksheet(sheet_name)
        sheet.write(0, 0, f"Rekapitulasi {position['position_name']}", title_fmt)
        sheet.write_row(2, 0, ["No", "Kandidat", "Suara", "Persentase"], header_fmt)
        for idx, result in enumerate(position["results"], start=3):
            sheet.write(idx, 0, result["number"], int_fmt)
            sheet.write(idx, 1, result["candidate_name"], text_fmt)
            sheet.write(idx, 2, result["votes"], int_fmt)
            sheet.write(idx, 3, result["percentage"] / 100, pct_fmt)
        sheet.set_column(0, 0, 8)
        sheet.set_column(1, 1, 28)
        sheet.set_column(2, 2, 12)
        sheet.set_column(3, 3, 14)

    workbook.close()
    buffer.seek(0)
    filename = f"{_safe_filename(recap['session_name'])}.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
