from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token, validate_token_claims
from app.models import AdminAccount, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/auth/login")

DbSession = Annotated[Session, Depends(get_db)]


def _get_subject_payload(token: str) -> dict:
    try:
        return decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


def get_current_user(db: DbSession, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    payload = _get_subject_payload(token)
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak memiliki sub")

    user = db.query(User).filter(User.nim == subject).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak ditemukan")
    return user


def get_optional_user(db: DbSession, authorization: str | None = Header(default=None)) -> User | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except ValueError:
        return None
    subject = payload.get("sub")
    if not subject:
        return None
    return db.query(User).filter(User.nim == subject).first()


def get_current_admin(db: DbSession, token: Annotated[str, Depends(admin_oauth2_scheme)]) -> AdminAccount:
    try:
        payload = validate_token_claims(token, required_claims={"role": "admin"})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak memiliki sub")
    admin = db.query(AdminAccount).filter(AdminAccount.username == subject).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin tidak ditemukan")
    return admin
