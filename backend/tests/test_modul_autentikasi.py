"""Pengujian Modul Autentikasi (registrasi, login, reset password mahasiswa)."""

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


def test_reset_password_dengan_kode_valid(client):
    register_student(client, "2141721099", password="password123")
    minta = client.post(f"{API}/auth/password/request-reset", json={"nim": "2141721099"})
    assert minta.status_code == 200
    konfirmasi = client.post(
        f"{API}/auth/password/confirm-reset",
        json={"nim": "2141721099", "code": "123456", "new_password": "passwordbaru1"},
    )
    assert konfirmasi.status_code == 200
    login = client.post(f"{API}/auth/login", json={"nim": "2141721099", "password": "passwordbaru1"})
    assert login.status_code == 200


def test_ambil_profil_dengan_token(client, student):
    response = client.get(f"{API}/auth/me", headers=student["auth"])
    assert response.status_code == 200
    assert response.json()["nim"] == student["nim"]
