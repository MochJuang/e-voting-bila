"""Pengujian unit Modul Face Service (algoritma inti pengenalan wajah).

Setiap test menguji satu fungsi/perilaku dari `FaceService`.
"""

from __future__ import annotations

import numpy as np
import pytest

from app.models.enums import FacePose, LivenessChallenge
from app.services.face_service import FaceService, FaceServiceError, face_service

from _util import frame_bytes


def test_pack_dan_unpack_embedding_roundtrip():
    v1 = np.random.rand(512).astype(np.float32)
    v2 = np.random.rand(512).astype(np.float32)
    blob = FaceService.pack_embeddings([v1, v2])
    matrix = FaceService.unpack_embeddings(blob)
    assert matrix.shape == (2, 512)


def test_unpack_kompatibel_format_lama_satu_vektor():
    v = np.random.rand(512).astype(np.float32)
    matrix = FaceService.unpack_embeddings(v.tobytes())
    assert matrix.shape == (1, 512)


def test_best_similarity_citra_sama_bernilai_satu():
    embedding = frame_bytes(seed=1)
    result = face_service.analyze(frame_bytes(seed=1))
    blob = FaceService.pack_embeddings([np.frombuffer(result.embedding, dtype=np.float32)])
    similarity = face_service.best_similarity(blob, result.embedding)
    assert similarity == pytest.approx(1.0, abs=1e-3)


def test_best_similarity_citra_berbeda_rendah():
    a = face_service.analyze(frame_bytes(seed=1)).embedding
    b = face_service.analyze(frame_bytes(seed=2)).embedding
    blob = FaceService.pack_embeddings([np.frombuffer(a, dtype=np.float32)])
    similarity = face_service.best_similarity(blob, b)
    assert similarity < 0.35


def test_decode_base64_valid_dan_strip_data_uri():
    raw = face_service.decode_base64("data:image/jpeg;base64,QUJD")
    assert raw == b"ABC"


def test_decode_base64_invalid_melempar_error():
    with pytest.raises(FaceServiceError):
        face_service.decode_base64("bukan-base64-valid!!")


def test_analyze_mode_fallback_menghasilkan_embedding():
    result = face_service.analyze(frame_bytes(seed=3))
    assert result.used_fallback is True
    assert result.face_count == 1
    assert len(result.embedding) > 0
    assert 0 <= result.quality_score <= 100


def test_enroll_poses_menerima_lima_pose():
    frames = [(pose, frame_bytes(seed=5)) for pose in FacePose]
    blob, results, quality, used_fallback = face_service.enroll_poses(frames)
    assert len(results) == 5
    assert all(r.accepted for r in results)
    assert FaceService.unpack_embeddings(blob).shape[0] == 5
    assert used_fallback is True


def test_verify_match_wajah_terdaftar_cocok():
    frames = [(pose, frame_bytes(seed=6)) for pose in FacePose]
    blob, *_ = face_service.enroll_poses(frames)
    _, similarity = face_service.verify_match(blob, frame_bytes(seed=6))
    assert similarity >= 0.35


def test_verify_match_wajah_lain_tidak_cocok():
    frames = [(pose, frame_bytes(seed=6)) for pose in FacePose]
    blob, *_ = face_service.enroll_poses(frames)
    _, similarity = face_service.verify_match(blob, frame_bytes(seed=42))
    assert similarity < 0.35


def test_evaluate_liveness_fallback_lolos_pada_kualitas_baik():
    passed, analysis, _ = face_service.evaluate_liveness(frame_bytes(seed=7), LivenessChallenge.TURN_LEFT)
    assert passed is True
    assert analysis.quality_score >= 60
