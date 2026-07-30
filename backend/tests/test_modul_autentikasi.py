"""Pengujian Modul Autentikasi (registrasi, login, ganti password mahasiswa)."""

from __future__ import annotations

from _util import API
from conftest import register_student


def test_registrasi_akun_mahasiswa_berhasil(client):
    response = register_student(client, "2141721099")
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["nim"] == "2141721099"
    assert body["access_token"]


def test_registrasi_nim_ganda_ditolak(client):
    register_student(client, "2141721099")
    response = register_student(client, "2141721099")
    assert response.status_code == 400


def test_login_mahasiswa_valid(client):
    register_student(client, "2141721099", password="password123")
    response = client.post(f"{API}/auth/login", json={"nim": "2141721099", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_password_salah_ditolak(client):
    register_student(client, "2141721099", password="password123")
    response = client.post(f"{API}/auth/login", json={"nim": "2141721099", "password": "salah999"})
    assert response.status_code == 401


def test_login_nim_tidak_terdaftar_ditolak(client):
    response = client.post(f"{API}/auth/login", json={"nim": "2141729999", "password": "password123"})
    assert response.status_code == 404


def test_ganti_password_mandiri_setelah_login(client):
    register_student(client, "2141721099", password="password123")
    login1 = client.post(f"{API}/auth/login", json={"nim": "2141721099", "password": "password123"})
    token = login1.json()["access_token"]

    ganti = client.post(
        f"{API}/auth/password/change",
        json={"current_password": "password123", "new_password": "passwordbaru1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ganti.status_code == 200, ganti.text

    login_baru = client.post(f"{API}/auth/login", json={"nim": "2141721099", "password": "passwordbaru1"})
    assert login_baru.status_code == 200
    login_lama = client.post(f"{API}/auth/login", json={"nim": "2141721099", "password": "password123"})
    assert login_lama.status_code == 401


def test_ganti_password_dengan_password_lama_salah_ditolak(client, student):
    response = client.post(
        f"{API}/auth/password/change",
        json={"current_password": "salahsekali", "new_password": "passwordbaru1"},
        headers=student["auth"],
    )
    assert response.status_code == 401


def test_ganti_password_tanpa_login_ditolak(client):
    response = client.post(
        f"{API}/auth/password/change",
        json={"current_password": "password123", "new_password": "passwordbaru1"},
    )
    assert response.status_code == 401


def test_ambil_profil_dengan_token(client, student):
    response = client.get(f"{API}/auth/me", headers=student["auth"])
    assert response.status_code == 200
    assert response.json()["nim"] == student["nim"]
