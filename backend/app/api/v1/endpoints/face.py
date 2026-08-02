import random

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DbSession, get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.models import FaceProfile, FaceVerificationLog, User
from app.models.enums import FacePose, LivenessChallenge, VerificationResult, VerifyStage
from app.schemas import FaceEnrollRequest, FaceEnrollResponse, FaceVerifyRequest, FaceVerifyResponse
from app.schemas.face import PoseEnrollResultResponse
from app.services.face_service import FaceService, FaceServiceError, face_service

router = APIRouter()


def _log_verification(
    db: DbSession,
    user: User,
    result: VerificationResult,
    similarity_score: float | None = None,
    liveness_score: float | None = None,
    reason: str | None = None,
    snapshot_base64: str | None = None,
):
    log = FaceVerificationLog(
        user_id=user.id,
        result=result,
        similarity_score=similarity_score,
        liveness_score=liveness_score,
        reason=reason,
        device_info=None,
        snapshot_base64=snapshot_base64,
    )
    db.add(log)


def _try_snapshot(image_base64: str | None) -> str | None:
    """Cuplikan frame wajah saat proses verifikasi/memilih, untuk audit terbatas.

    Kegagalan dekode/kompresi tidak boleh menggagalkan alur verifikasi — kembalikan
    None saja bila terjadi masalah.
    """
    if not image_base64:
        return None
    try:
        image_bytes = face_service.decode_base64(image_base64)
        return face_service.to_display_photo(image_bytes)
    except FaceServiceError:
        return None


def _reject_if_face_registered_elsewhere(db: DbSession, new_blob: bytes, exclude_user_id: int) -> None:
    """Tolak registrasi bila wajah ini sudah terdaftar pada akun mahasiswa lain.

    Mencegah satu wajah dipakai untuk mendaftarkan banyak NIM (mis. berbagi wajah
    dengan orang lain agar bisa memilih ganda). NIM pemilik lain sengaja tidak
    diungkap ke pemanggil untuk menjaga privasi — cukup ditolak.
    """
    candidate_matrix = FaceService.unpack_embeddings(new_blob)
    other_profiles = db.query(FaceProfile).filter(FaceProfile.user_id != exclude_user_id).all()
    for other_profile in other_profiles:
        for row in candidate_matrix:
            similarity = face_service.best_similarity(other_profile.embedding, row.tobytes())
            if similarity >= settings.face_match_threshold:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Wajah ini terindikasi sudah terdaftar pada akun mahasiswa lain. "
                        "Registrasi ditolak untuk mencegah satu wajah dipakai di banyak akun. "
                        "Hubungi panitia jika Anda yakin ini adalah kesalahan."
                    ),
                )


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

    _reject_if_face_registered_elsewhere(db, blob, exclude_user_id=current_user.id)

    version = "insightface-multipose-v1" if not used_fallback else "fallback-multipose-v1"

    # Foto referensi yang ditampilkan kembali: pakai pose tengah (paling representatif),
    # fallback ke frame pertama bila pose tengah tidak dikirim.
    reference_bytes = next((b for pose, b in frames if pose == FacePose.CENTER), frames[0][1])
    photo_base64 = face_service.to_display_photo(reference_bytes)

    # Cermin blob dalam bentuk array angka biasa (bukan biner) — sama persis isinya,
    # cuma agar bisa diinspeksi/dibaca langsung; pencocokan tetap memakai `embedding` (blob).
    embedding_vector = FaceService.unpack_embeddings(blob).tolist()

    profile = db.query(FaceProfile).filter(FaceProfile.user_id == current_user.id).first()
    if profile:
        profile.embedding = blob
        profile.embedding_vector = embedding_vector
        profile.embedding_version = version
        profile.quality_score = quality
        profile.photo_base64 = photo_base64
    else:
        profile = FaceProfile(
            user_id=current_user.id,
            embedding=blob,
            embedding_vector=embedding_vector,
            embedding_version=version,
            quality_score=quality,
            photo_base64=photo_base64,
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


@router.post("/verify", response_model=FaceVerifyResponse)
def verify_face(payload: FaceVerifyRequest, db: DbSession, current_user: User = Depends(get_current_user)):
    if current_user.nim != payload.nim:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak bisa verifikasi untuk NIM lain")

    # Tidak ada batas percobaan/penguncian akun — mahasiswa boleh mengulang verifikasi
    # wajah & liveness tanpa batas hingga berhasil.
    invalid_count = _invalid_count(db, current_user)

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
    # Timeout dari client: catat sebagai percobaan gagal (untuk statistik/audit saja).
    if payload.timed_out:
        _log_verification(
            db,
            current_user,
            VerificationResult.INVALID,
            reason="Liveness timeout",
            snapshot_base64=_try_snapshot(payload.image_base64),
        )
        db.commit()
        return FaceVerifyResponse(
            stage=VerifyStage.LIVENESS,
            matched=True,
            result=VerificationResult.INVALID,
            challenge=payload.challenge,
            retry_count=invalid_count + 1,
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
        snapshot_base64=face_service.to_display_photo(image_bytes),
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
