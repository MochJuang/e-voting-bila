from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel
from app.schemas.enums import AccessMode


class RegisterRequest(BaseModel):
    nim: str = Field(min_length=5, max_length=20)
    nama: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    kelas: str = Field(min_length=1, max_length=50)


class LoginRequest(BaseModel):
    nim: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    nim: str = Field(min_length=5, max_length=20)


class PasswordResetConfirmRequest(BaseModel):
    nim: str = Field(min_length=5, max_length=20)
    code: str = Field(min_length=4, max_length=20)
    new_password: str = Field(min_length=8, max_length=128)


class AuthUserResponse(ORMModel):
    id: int
    nim: str
    nama: str
    email: str | None = None
    kelas: str | None = None
    mode_akses: AccessMode
    face_enrolled: bool
    has_voted: bool
    is_locked: bool


class AuthSessionResponse(BaseModel):
    user: AuthUserResponse
    access_token: str | None = None
    token_type: str | None = "bearer"

