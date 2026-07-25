"""Pengujian Modul Pemungutan Suara (booth voting & pencegahan suara ganda)."""

from __future__ import annotations

from _util import API


def _submit(client, headers, nim, token, election, selections=None):
    if selections is None:
        selections = [{"position_id": election["position_id"], "candidate_id": election["candidate_id"]}]
    return client.post(
        f"{API}/votes/submit",
        json={
            "session_id": election["session_id"],
            "nim": nim,
            "verification_token": token,
            "selections": selections,
        },
        headers=headers,
    )


def test_ambil_sesi_pemilihan_aktif(client, election):
    response = client.get(f"{API}/election/active")
    assert response.status_code == 200
    assert len(response.json()["positions"]) >= 1


def test_voting_berhasil_setelah_verifikasi(client, student, face_verified_token, election):
    response = _submit(client, student["auth"], student["nim"], face_verified_token, election)
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_voting_ganda_ditolak(client, student, face_verified_token, election):
    first = _submit(client, student["auth"], student["nim"], face_verified_token, election)
    assert first.status_code == 200
    second = _submit(client, student["auth"], student["nim"], face_verified_token, election)
    assert second.status_code == 400


def test_voting_tanpa_semua_jabatan_ditolak(client, student, face_verified_token, election):
    response = _submit(client, student["auth"], student["nim"], face_verified_token, election, selections=[])
    assert response.status_code == 400


def test_voting_token_verifikasi_tidak_valid_ditolak(client, student, election):
    response = _submit(client, student["auth"], student["nim"], "token.tidak.valid", election)
    assert response.status_code == 401
