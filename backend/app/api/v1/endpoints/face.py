from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DbSession, get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.models import FaceProfile, FaceVerificationLog, User
from app.models.enums import VerificationResult
from app.schemas import FaceEnrollRequest, FaceEnrollResponse, FaceVerifyRequest, FaceVerifyResponse
from app.services.face_service import FaceServiceError, face_service

router = APIRouter()


def _log_verification(
    db: DbSession,
    user: User,
    result: VerificationResult,
    similarity_score: float | None = None,
    liveness_score: float | None = None,
    reason: str | None = None,
):
    log = FaceVerificationLog(
        user_id=user.id,
        result=result,
        similarity_score=similarity_score,
        liveness_score=liveness_score,
        reason=reason,
        device_info=None,
    )
    db.add(log)


@router.post("/enroll", response_model=FaceEnrollResponse)
def enroll_face(payload: FaceEnrollRequest, db: DbSession, current_user: User = Depends(get_current_user)):
    if current_user.nim != payload.nim:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak bisa enroll untuk NIM lain")

    try:
        image_bytes = face_service.decode_base64(payload.image_base64)
        result = face_service.enroll(image_bytes)
    except FaceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    profile = db.query(FaceProfile).filter(FaceProfile.user_id == current_user.id).first()
    if profile:
        profile.embedding = result.embedding
        profile.embedding_version = "insightface-v1" if not result.used_fallback else "fallback-embed-v1"
        profile.quality_score = result.quality_score
    else:
        profile = FaceProfile(
            user_id=current_user.id,
            embedding=result.embedding,
            embedding_version="insightface-v1" if not result.used_fallback else "fallback-embed-v1",
            quality_score=result.quality_score,
        )
        db.add(profile)

    current_user.face_enrolled = True
    db.commit()

    return FaceEnrollResponse(
        success=True,
        face_enrolled=True,
        quality_score=result.quality_score,
        message="Wajah berhasil diregistrasi." if not result.used_fallback else "Wajah berhasil diregistrasi dengan mode fallback.",
    )


@router.post("/verify", response_model=FaceVerifyResponse)
def verify_face(payload: FaceVerifyRequest, db: DbSession, current_user: User = Depends(get_current_user)):
    if current_user.nim != payload.nim:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak bisa verifikasi untuk NIM lain")

    invalid_count = (
        db.query(FaceVerificationLog)
        .filter(FaceVerificationLog.user_id == current_user.id, FaceVerificationLog.result == VerificationResult.INVALID)
        .count()
    )
    if current_user.is_locked or invalid_count >= settings.face_max_retries:
        current_user.is_locked = True
        _log_verification(db, current_user, VerificationResult.LOCKED, reason="Percobaan melebihi batas")
        db.commit()
        return FaceVerifyResponse(
            verified=False,
            result=VerificationResult.LOCKED,
            similarity_score=None,
            liveness_score=None,
            retry_count=invalid_count,
            lock_applied=True,
            verification_token=None,
            message="Akun dikunci sementara. Hubungi panitia untuk verifikasi manual.",
        )

    if not current_user.face_enrolled:
        _log_verification(db, current_user, VerificationResult.INVALID, reason="Wajah belum terdaftar")
        db.commit()
        return FaceVerifyResponse(
            verified=False,
            result=VerificationResult.INVALID,
            retry_count=invalid_count + 1,
            message="Wajah belum terdaftar. Lakukan registrasi wajah terlebih dahulu.",
        )

    profile = db.query(FaceProfile).filter(FaceProfile.user_id == current_user.id).first()
    if not profile:
        _log_verification(db, current_user, VerificationResult.INVALID, reason="Profil wajah tidak ditemukan")
        db.commit()
        return FaceVerifyResponse(
            verified=False,
            result=VerificationResult.INVALID,
            retry_count=invalid_count + 1,
            message="Profil wajah belum terdaftar. Silakan registrasi wajah terlebih dahulu.",
        )

    try:
        image_bytes = face_service.decode_base64(payload.image_base64)
        result = face_service.verify(profile.embedding, image_bytes)
    except FaceServiceError as exc:
        _log_verification(db, current_user, VerificationResult.INVALID, reason=str(exc))
        db.commit()
        return FaceVerifyResponse(
            verified=False,
            result=VerificationResult.INVALID,
            retry_count=invalid_count + 1,
            message=str(exc),
        )

    similarity_score = round(result.similarity or 0.0, 3)
    liveness_score = result.liveness_score
    if similarity_score < settings.face_match_threshold or liveness_score < 0.5:
        _log_verification(
            db,
            current_user,
            VerificationResult.INVALID,
            similarity_score=similarity_score,
            liveness_score=liveness_score,
            reason="Similarity atau liveness di bawah threshold",
        )
        db.commit()
        return FaceVerifyResponse(
            verified=False,
            result=VerificationResult.INVALID,
            similarity_score=similarity_score,
            liveness_score=liveness_score,
            retry_count=invalid_count + 1,
            lock_applied=False,
            verification_token=None,
            message="Verifikasi wajah gagal. Coba lagi dengan kondisi wajah yang lebih jelas.",
        )

    _log_verification(
        db,
        current_user,
        VerificationResult.VALID,
        similarity_score=similarity_score,
        liveness_score=liveness_score,
        reason="Verifikasi berhasil",
    )
    db.commit()

    token = create_access_token(current_user.nim, expires_minutes=15, extra_claims={"purpose": "face_verified"})
    return FaceVerifyResponse(
        verified=True,
        result=VerificationResult.VALID,
        similarity_score=similarity_score,
        liveness_score=liveness_score,
        retry_count=invalid_count,
        lock_applied=False,
        verification_token=token,
        message="Verifikasi wajah berhasil.",
    )
