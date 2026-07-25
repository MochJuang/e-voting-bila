"""Pengujian Modul Keamanan (proteksi akses, hashing, isolasi identitas)."""

from __future__ import annotations

from app.core.security import verify_password
from app.models import User

from _util import API, make_face_b64
from conftest import register_student


def test_password_disimpan_dalam_bentuk_hash(client, db):
    register_student(client, "2141721099", password="password123")
    user = db.query(User).filter(User.nim == "2141721099").first()
    assert user is not None
    assert user.password_hash != "password123"
    assert verify_password("password123", user.password_hash) is True


def test_verifikasi_untuk_nim_lain_ditolak(client, student):
    response = client.post(
        f"{API}/face/verify",
        json={"nim": "2141721002", "image_base64": make_face_b64(1), "stage": "match"},
        headers=student["auth"],
    )
    assert response.status_code == 403


def test_endpoint_terproteksi_tanpa_token_ditolak(client):
    response = client.get(f"{API}/voters/me")
    assert response.status_code == 401


def test_token_mahasiswa_tidak_bisa_akses_dashboard_admin(client, student):
    response = client.get(f"{API}/admin/dashboard", headers=student["auth"])
    assert response.status_code == 401
