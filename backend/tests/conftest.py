"""Fixtures pytest: DB SQLite in-memory, TestClient, mode fallback wajah, dan helper token."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registrasi seluruh model ke Base.metadata)
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app
from app.services.face_service import face_service

from _util import API, make_face_b64


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture()
def Session(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db(Session):
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def force_face_fallback():
    """Paksa mode fallback: cepat, deterministik, tanpa unduh model InsightFace."""
    face_service._model_loaded = True
    face_service._model = None
    face_service._model_error = "forced-fallback-in-tests"
    yield


@pytest.fixture()
def client(Session):
    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# --------------------------------------------------------------------------- #
# Helper fixtures
# --------------------------------------------------------------------------- #
def register_student(client, nim: str = "2141721099", password: str = "password123"):
    return client.post(
        f"{API}/auth/register",
        json={
            "nim": nim,
            "nama": "Mahasiswa Uji",
            "email": f"{nim}@nusaputra.ac.id",
            "password": password,
            "kelas": "TI-3A",
        },
    )


@pytest.fixture()
def student(client):
    nim = "2141721099"
    response = register_student(client, nim)
    token = response.json()["access_token"]
    return {"nim": nim, "token": token, "auth": {"Authorization": f"Bearer {token}"}}


@pytest.fixture()
def enrolled_student(client, student):
    """Mahasiswa yang sudah registrasi wajah (5 pose). Mengembalikan juga frame acuannya."""
    frame = make_face_b64(seed=1)
    frames = [{"pose": pose, "image_base64": frame} for pose in ("center", "up", "right", "down", "left")]
    response = client.post(
        f"{API}/face/enroll",
        json={"nim": student["nim"], "frames": frames},
        headers=student["auth"],
    )
    assert response.status_code == 200, response.text
    return {**student, "frame": frame}


@pytest.fixture()
def face_verified_token(student):
    """Token hasil verifikasi wajah (claim purpose=face_verified) untuk uji voting."""
    return create_access_token(student["nim"], expires_minutes=15, extra_claims={"purpose": "face_verified"})


@pytest.fixture()
def election(db):
    """Seed sesi pemilihan aktif + jabatan + kandidat, kembalikan id-nya."""
    from app.services.mock_helpers import ensure_default_election_data

    session = ensure_default_election_data(db)
    position = list(session.positions)[0]
    candidate = list(position.candidates)[0]
    return {
        "session_id": session.id,
        "position_id": position.id,
        "candidate_id": candidate.id,
    }
