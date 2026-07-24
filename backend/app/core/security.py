from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt punya batas 72 byte untuk password mentah. bcrypt_sha256
# men-hash dulu input yang panjang, jadi login/registrasi tetap aman.
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str, expires_minutes: int | None = None, extra_claims: dict | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.jwt_access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
    except JWTError as exc:
        raise ValueError("Token tidak valid") from exc


def validate_token_claims(
    token: str,
    *,
    expected_subject: str | None = None,
    required_claims: dict | None = None,
) -> dict:
    payload = decode_access_token(token)
    if expected_subject is not None and payload.get("sub") != expected_subject:
        raise ValueError("Token tidak sesuai subjek yang diharapkan")

    required_claims = required_claims or {}
    for key, expected in required_claims.items():
        if payload.get(key) != expected:
            raise ValueError(f"Token tidak memenuhi claim {key}")

    return payload
