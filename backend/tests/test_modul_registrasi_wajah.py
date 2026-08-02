"""Pengujian Modul Registrasi Wajah (enrollment 5 pose)."""

from __future__ import annotations

import numpy as np

from _util import API, make_face_b64
from conftest import register_student

from app.models import FaceProfile
from app.services.face_service import FaceService


def _five_frames(seed: int = 1):
    frame = make_face_b64(seed)
    return [{"pose": pose, "image_base64": frame} for pose in ("center", "up", "right", "down", "left")]


def test_registrasi_wajah_lima_pose_berhasil(client, student):
    response = client.post(
        f"{API}/face/enroll",
        json={"nim": student["nim"], "frames": _five_frames()},
        headers=student["auth"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["face_enrolled"] is True
    assert len(body["poses"]) == 5
    assert all(p["accepted"] for p in body["poses"])


def test_embedding_vector_tersimpan_sebagai_array_bukan_blob(client, db, student):
    response = client.post(
        f"{API}/face/enroll",
        json={"nim": student["nim"], "frames": _five_frames()},
        headers=student["auth"],
    )
    assert response.status_code == 200

    profile = db.query(FaceProfile).first()
    assert isinstance(profile.embedding_vector, list)
    assert len(profile.embedding_vector) == 5  # 5 pose
    assert all(isinstance(v, float) for v in profile.embedding_vector[0])

    # Isinya harus identik (secara numerik) dengan hasil unpack blob `embedding` (sumber
    # kebenaran pencocokan). Dibandingkan dengan toleransi, bukan `==` ketat — nilai float
    # yang lolos round-trip JSON (mis. via MySQL) bisa beda representasi float64 vs float32
    # walau nilainya sama persis pada presisi aslinya.
    expected = FaceService.unpack_embeddings(profile.embedding)
    actual = np.array(profile.embedding_vector, dtype=np.float32)
    assert np.allclose(actual, expected, atol=1e-5)


def test_status_face_enrolled_terupdate_setelah_registrasi(client, enrolled_student):
    response = client.get(f"{API}/voters/me/status", headers=enrolled_student["auth"])
    assert response.status_code == 200
    body = response.json()
    assert body["face_enrolled"] is True
    assert body["next_step"] == "verifikasi wajah"


def test_registrasi_untuk_nim_lain_ditolak(client, student):
    response = client.post(
        f"{API}/face/enroll",
        json={"nim": "2141721002", "frames": _five_frames()},
        headers=student["auth"],
    )
    assert response.status_code == 403


def test_registrasi_dengan_citra_rusak_ditolak(client, student):
    frames = [{"pose": pose, "image_base64": "data:image/jpeg;base64,QUJD"} for pose in ("center", "up", "right", "down", "left")]
    response = client.post(
        f"{API}/face/enroll",
        json={"nim": student["nim"], "frames": frames},
        headers=student["auth"],
    )
    assert response.status_code == 400


def test_wajah_yang_sama_ditolak_saat_didaftarkan_akun_lain(client, enrolled_student):
    """Satu wajah tidak boleh terdaftar pada lebih dari satu NIM."""
    kedua = register_student(client, "2141721077")
    token_kedua = kedua.json()["access_token"]

    response = client.post(
        f"{API}/face/enroll",
        # seed=1 sama persis dengan wajah milik enrolled_student
        json={"nim": "2141721077", "frames": _five_frames(seed=1)},
        headers={"Authorization": f"Bearer {token_kedua}"},
    )
    assert response.status_code == 400
    assert "akun mahasiswa lain" in response.json()["detail"]


def test_wajah_berbeda_tetap_bisa_didaftarkan_akun_lain(client, enrolled_student):
    """Memastikan validasi anti-duplikasi tidak salah menolak wajah yang benar-benar berbeda."""
    kedua = register_student(client, "2141721078")
    token_kedua = kedua.json()["access_token"]

    response = client.post(
        f"{API}/face/enroll",
        json={"nim": "2141721078", "frames": _five_frames(seed=99)},
        headers={"Authorization": f"Bearer {token_kedua}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["face_enrolled"] is True
