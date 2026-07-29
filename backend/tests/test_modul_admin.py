"""Pengujian Modul Panitia/Admin (login admin, dashboard, rekapitulasi)."""

from __future__ import annotations

import pytest

from _util import API
from conftest import register_student


@pytest.fixture()
def admin_auth(client):
    response = client.post(f"{API}/admin/auth/login", json={"username": "panitia1", "password": "PanitiaIT123!"})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_admin_valid(client):
    response = client.post(f"{API}/admin/auth/login", json={"username": "panitia1", "password": "PanitiaIT123!"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_admin_password_salah_ditolak(client):
    response = client.post(f"{API}/admin/auth/login", json={"username": "panitia1", "password": "salah"})
    assert response.status_code == 401


def test_dashboard_panitia_menampilkan_statistik(client, admin_auth):
    response = client.get(f"{API}/admin/dashboard", headers=admin_auth)
    assert response.status_code == 200
    stats = response.json()["stats"]
    assert "total_dpt" in stats
    assert "sudah_memilih" in stats


def test_dashboard_tanpa_token_admin_ditolak(client):
    response = client.get(f"{API}/admin/dashboard")
    assert response.status_code == 401


def test_bulk_create_mahasiswa(client, admin_auth):
    register_student(client, "2141721001")  # sudah ada -> harus skipped
    response = client.post(
        f"{API}/admin/voters/bulk",
        json={
            "voters": [
                {"nim": "2141721001", "nama": "Duplikat"},
                {"nim": "2141721201", "nama": "Andi", "kelas": "TI-3A", "mode_akses": "mandiri"},
                {"nim": "2141721202", "nama": "Bunga", "kelas": "SI-2B", "mode_akses": "admin_assisted"},
            ]
        },
        headers=admin_auth,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["created"] == 2
    assert body["skipped"] == 1


def test_reset_password_mahasiswa_oleh_admin(client, admin_auth):
    register_student(client, "2141721088", password="password123")
    reset = client.patch(
        f"{API}/admin/voters/2141721088",
        json={"nim": "2141721088", "nama": "Mahasiswa Uji", "mode_akses": "mandiri", "password": "passwordbaru9"},
        headers=admin_auth,
    )
    assert reset.status_code == 200, reset.text
    assert client.post(f"{API}/auth/login", json={"nim": "2141721088", "password": "passwordbaru9"}).status_code == 200
    assert client.post(f"{API}/auth/login", json={"nim": "2141721088", "password": "password123"}).status_code == 401


def test_kelola_akun_admin(client, admin_auth):
    created = client.post(
        f"{API}/admin/accounts",
        json={"username": "panitia3", "password": "rahasia6", "role": "admin"},
        headers=admin_auth,
    )
    assert created.status_code == 200, created.text
    account_id = created.json()["id"]

    assert client.post(f"{API}/admin/auth/login", json={"username": "panitia3", "password": "rahasia6"}).status_code == 200

    updated = client.patch(
        f"{API}/admin/accounts/{account_id}",
        json={"password": "barubaru7"},
        headers=admin_auth,
    )
    assert updated.status_code == 200
    assert client.post(f"{API}/admin/auth/login", json={"username": "panitia3", "password": "barubaru7"}).status_code == 200
    assert client.post(f"{API}/admin/auth/login", json={"username": "panitia3", "password": "rahasia6"}).status_code == 401

    deleted = client.delete(f"{API}/admin/accounts/{account_id}", headers=admin_auth)
    assert deleted.status_code == 200


def test_edit_kelas_dan_mode_akses_mahasiswa(client, admin_auth):
    register_student(client, "2141721077")
    response = client.patch(
        f"{API}/admin/voters/2141721077",
        json={
            "nim": "2141721077",
            "nama": "Mahasiswa Uji",
            "kelas": "TI-4C",
            "mode_akses": "admin_assisted",
            "email": "2141721077@nusaputra.ac.id",
        },
        headers=admin_auth,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["kelas"] == "TI-4C"
    assert body["mode_akses"] == "admin_assisted"
