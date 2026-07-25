"""Pengujian Modul Panitia/Admin (login admin, dashboard, rekapitulasi)."""

from __future__ import annotations

import pytest

from _util import API


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
