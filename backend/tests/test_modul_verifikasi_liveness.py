"""Pengujian Modul Verifikasi Wajah & Liveness (alur realtime bertahap)."""

from __future__ import annotations

from _util import API, make_face_b64

VALID_CHALLENGES = {"smile", "turn_left", "turn_right"}


def _verify(client, headers, nim, frame, stage="match", challenge=None, timed_out=False):
    return client.post(
        f"{API}/face/verify",
        json={
            "nim": nim,
            "image_base64": frame,
            "stage": stage,
            "challenge": challenge,
            "timed_out": timed_out,
        },
        headers=headers,
    )


def test_verifikasi_ditolak_bila_belum_registrasi(client, student):
    frame = make_face_b64(seed=1)
    response = _verify(client, student["auth"], student["nim"], frame)
    assert response.status_code == 200
    body = response.json()
    assert body["verified"] is False
    assert body["result"] == "invalid"


def test_pencocokan_wajah_realtime_cocok(client, enrolled_student):
    response = _verify(client, enrolled_student["auth"], enrolled_student["nim"], enrolled_student["frame"])
    assert response.status_code == 200
    body = response.json()
    assert body["matched"] is True
    assert body["challenge"] in VALID_CHALLENGES
    assert body["similarity_score"] >= 0.35


def test_wajah_berbeda_tidak_cocok(client, enrolled_student):
    frame_lain = make_face_b64(seed=42)
    response = _verify(client, enrolled_student["auth"], enrolled_student["nim"], frame_lain)
    body = response.json()
    assert body["matched"] is False


def test_liveness_valid_menerbitkan_token(client, enrolled_student):
    match = _verify(client, enrolled_student["auth"], enrolled_student["nim"], enrolled_student["frame"]).json()
    challenge = match["challenge"]
    liveness = _verify(
        client,
        enrolled_student["auth"],
        enrolled_student["nim"],
        enrolled_student["frame"],
        stage="liveness",
        challenge=challenge,
    )
    body = liveness.json()
    assert body["verified"] is True
    assert body["liveness_passed"] is True
    assert body["verification_token"]


def test_akun_terkunci_setelah_percobaan_gagal(client, enrolled_student):
    body = None
    for _ in range(3):
        body = _verify(
            client,
            enrolled_student["auth"],
            enrolled_student["nim"],
            enrolled_student["frame"],
            stage="liveness",
            challenge="smile",
            timed_out=True,
        ).json()
    assert body["result"] == "locked"
    assert body["lock_applied"] is True
