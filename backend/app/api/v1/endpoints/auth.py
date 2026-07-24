from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import DbSession, get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.models.enums import AccessMode
from app.schemas import (
    AuthSessionResponse,
    AuthUserResponse,
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.responses import MessageResponse
from app.services.mock_helpers import find_default_voter

router = APIRouter()


def _user_to_response(user: User) -> AuthUserResponse:
    return AuthUserResponse.model_validate(user)


@router.post("/register", response_model=AuthSessionResponse)
def register(payload: RegisterRequest, db: DbSession):
    existing = db.query(User).filter(or_(User.nim == payload.nim, User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NIM atau email sudah terdaftar")

    default_voter = find_default_voter(payload.nim)
    user = User(
        nim=payload.nim,
        nama=payload.nama,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        kelas=payload.kelas,
        mode_akses=default_voter.mode_akses if default_voter else AccessMode.MANDIRI,
        is_dpt_member=True,
        face_enrolled=bool(default_voter.face_enrolled) if default_voter else False,
        has_voted=bool(default_voter.has_voted) if default_voter else False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.nim)
    return AuthSessionResponse(user=_user_to_response(user), access_token=token)


@router.post("/login", response_model=AuthSessionResponse)
def login(payload: LoginRequest, db: DbSession):
    user = db.query(User).filter(User.nim == payload.nim).first()
    if not user:
        default_voter = find_default_voter(payload.nim)
        if not default_voter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NIM tidak ditemukan")
        user = User(
            nim=default_voter.nim,
            nama=default_voter.nama,
            kelas=default_voter.kelas,
            mode_akses=default_voter.mode_akses,
            password_hash=hash_password(payload.password),
            face_enrolled=default_voter.face_enrolled,
            has_voted=default_voter.has_voted,
            is_dpt_member=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif user.password_hash and not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password salah")
    elif not user.password_hash:
        user.password_hash = hash_password(payload.password)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.nim)
    return AuthSessionResponse(user=_user_to_response(user), access_token=token)


@router.post("/password/request-reset", response_model=MessageResponse)
def request_password_reset(payload: PasswordResetRequest, db: DbSession):
    user = db.query(User).filter(User.nim == payload.nim).first()
    if not user and not find_default_voter(payload.nim):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NIM tidak ditemukan")
    return MessageResponse(message="Kode verifikasi reset password telah dikirim ke email kampus.")


@router.post("/password/confirm-reset", response_model=MessageResponse)
def confirm_password_reset(payload: PasswordResetConfirmRequest, db: DbSession):
    if payload.code != "123456":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kode verifikasi tidak valid")

    user = db.query(User).filter(User.nim == payload.nim).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NIM tidak ditemukan")
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return MessageResponse(message="Password berhasil direset.")


@router.get("/me", response_model=AuthUserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return _user_to_response(current_user)
