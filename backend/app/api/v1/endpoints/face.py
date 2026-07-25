import random

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DbSession, get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.models import FaceProfile, FaceVerificationLog, User
from app.models.enums import LivenessChallenge, VerificationResult, VerifyStage
from app.schemas import FaceEnrollRequest, FaceEnrollResponse, FaceVerifyRequest, FaceVerifyResponse
from app.schemas.face import PoseEnrollResultResponse
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


def _invalid_count(db: DbSession, user: User) -> int:
    return (
        db.query(FaceVerificationLog)
        .filter(
            FaceVerificationLog.user_id == user.id,
            FaceVerificationLog.result == VerificationResult.INVALID,
        )
        .count()
    )


@router.post("/enroll", response_model=FaceEnrollResponse)
def enroll_face(payload: FaceEnrollRequest, db: DbSession, current_user: User = Depends(get_current_user)):
    if current_user.nim != payload.nim:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak bisa enroll untuk NIM lain")

    try:
        frames = [(frame.pose, face_service.decode_base64(frame.image_base64)) for frame in payload.frames]
        blob, pose_results, quality, used_fallback = face_service.enroll_poses(frames)
    except FaceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    version = "insightface-multipose-v1" if not used_fallback else "fallback-multipose-v1"

    profile = db.query(FaceProfile).filter(FaceProfile.user_id == current_user.id).first()
    if profile:
        profile.embedding = blob
        profile.embedding_version = version
        profile.quality_score = quality
    else:
        profile = FaceProfile(
            user_id=current_user.id,
            embedding=blob,
            embedding_version=version,
            quality_score=quality,
        )
        db.add(profile)

    current_user.face_enrolled = True
    db.commit()

    return FaceEnrollResponse(
        success=True,
        face_enrolled=True,
        quality_score=quality,
        poses=[
            PoseEnrollResultResponse(
                pose=item.pose,
                accepted=item.accepted,
                quality_score=item.quality_score,
                message=item.message,
            )
            for item in pose_results
        ],
        message="Registrasi wajah berhasil (5 pose)." if not used_fallback else "Registrasi wajah berhasil (mode fallback).",
    )


def _locked_response(db: DbSession, user: User, stage: VerifyStage, invalid_count: int) -> FaceVerifyResponse:
    user.is_locked = True
    _log_verification(db, user, VerificationResult.LOCKED, reason="Percobaan melebihi batas")
    db.commit()
    return FaceVerifyResponse(
        stage=stage,
        verified=False,
        matched=False,
        result=VerificationResult.LOCKED,
        retry_count=invalid_count,
        lock_applied=True,
        message="Akun dikunci sementara. Hubungi panitia untuk verifikasi manual.",
    )


@router.post("/verify", response_model=FaceVerifyResponse)
def verify_face(payload: FaceVerifyRequest, db: DbSession, current_user: User = Depends(get_current_user)):
    if current_user.nim != payload.nim:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak bisa verifikasi untuk NIM lain")

    invalid_count = _invalid_count(db, current_user)
    if current_user.is_locked or invalid_count >= settings.face_max_retries:
        return _locked_response(db, current_user, payload.stage, invalid_count)

    if not current_user.face_enrolled:
        return FaceVerifyResponse(
            stage=payload.stage,
            result=VerificationResult.INVALID,
            message="Wajah belum terdaftar. Lakukan registrasi wajah terlebih dahulu.",
        )

    profile = db.query(FaceProfile).filter(FaceProfile.user_id == current_user.id).first()
    if not profile:
        return FaceVerifyResponse(
            stage=payload.stage,
            result=VerificationResult.INVALID,
            message="Profil wajah belum terdaftar. Silakan registrasi wajah terlebih dahulu.",
        )

    # --------------------------------------------------------------- #
    # STAGE 1: pencocokan wajah (streaming, tidak dicatat per-frame)
    # --------------------------------------------------------------- #
    if payload.stage == VerifyStage.MATCH:
        try:
            image_bytes = face_service.decode_base64(payload.image_base64)
            analysis, similarity = face_service.verify_match(profile.embedding, image_bytes)
        except FaceServiceError as exc:
            return FaceVerifyResponse(
                stage=VerifyStage.MATCH,
                result=VerificationResult.INVALID,
                retry_count=invalid_count,
                message=str(exc),
            )

        matched = similarity >= settings.face_match_threshold and analysis.liveness_score >= settings.liveness_min_score
        if not matched:
            return FaceVerifyResponse(
                stage=VerifyStage.MATCH,
                matched=False,
                result=VerificationResult.INVALID,
                similarity_score=similarity,
                liveness_score=analysis.liveness_score,
                retry_count=invalid_count,
                message="Mencari kecocokan wajah… posisikan wajah di tengah bingkai.",
            )

        challenge = random.choice(list(LivenessChallenge))
        return FaceVerifyResponse(
            stage=VerifyStage.MATCH,
            matched=True,
            result=VerificationResult.VALID,
            similarity_score=similarity,
            liveness_score=analysis.liveness_score,
            challenge=challenge,
            retry_count=invalid_count,
            message="Wajah cocok. Lakukan gerakan liveness.",
        )

    # --------------------------------------------------------------- #
    # STAGE 2: liveness challenge
    # --------------------------------------------------------------- #
    # Timeout dari client: catat sebagai percobaan gagal (untuk anti-abuse / lock).
    if payload.timed_out:
        _log_verification(
            db,
            current_user,
            VerificationResult.INVALID,
            reason="Liveness timeout",
        )
        new_invalid = invalid_count + 1
        if new_invalid >= settings.face_max_retries:
            return _locked_response(db, current_user, VerifyStage.LIVENESS, new_invalid)
        db.commit()
        return FaceVerifyResponse(
            stage=VerifyStage.LIVENESS,
            matched=True,
            result=VerificationResult.INVALID,
            challenge=payload.challenge,
            retry_count=new_invalid,
            message="Waktu liveness habis. Silakan coba lagi.",
        )

    if payload.challenge is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Challenge liveness wajib diisi")

    try:
        image_bytes = face_service.decode_base64(payload.image_base64)
        passed, analysis, detail = face_service.evaluate_liveness(image_bytes, payload.challenge)
        similarity = face_service.best_similarity(
            profile.embedding,
            analysis.embedding,
        )
    except FaceServiceError as exc:
        return FaceVerifyResponse(
            stage=VerifyStage.LIVENESS,
            matched=True,
            result=VerificationResult.INVALID,
            challenge=payload.challenge,
            retry_count=invalid_count,
            message=str(exc),
        )

    still_matched = similarity >= settings.face_match_threshold
    if not (passed and still_matched):
        return FaceVerifyResponse(
            stage=VerifyStage.LIVENESS,
            matched=still_matched,
            result=VerificationResult.INVALID,
            similarity_score=similarity,
            liveness_score=analysis.liveness_score,
            challenge=payload.challenge,
            liveness_passed=False,
            retry_count=invalid_count,
            message=detail if still_matched else "Wajah tidak lagi cocok, posisikan wajah kembali.",
        )

    _log_verification(
        db,
        current_user,
        VerificationResult.VALID,
        similarity_score=similarity,
        liveness_score=analysis.liveness_score,
        reason=f"Verifikasi berhasil (liveness: {payload.challenge.value})",
    )
    db.commit()

    token = create_access_token(current_user.nim, expires_minutes=15, extra_claims={"purpose": "face_verified"})
    return FaceVerifyResponse(
        stage=VerifyStage.LIVENESS,
        verified=True,
        matched=True,
        result=VerificationResult.VALID,
        similarity_score=similarity,
        liveness_score=analysis.liveness_score,
        challenge=payload.challenge,
        liveness_passed=True,
        retry_count=invalid_count,
        verification_token=token,
        message="Verifikasi wajah & liveness berhasil.",
    )
