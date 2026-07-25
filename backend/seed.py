"""Seed data awal untuk development.

Mengisi database dengan sesi pemilihan, jabatan, kandidat, akun mahasiswa (DPT),
dan akun admin/panitia default. Aman dijalankan berulang (idempotent) — data yang
sudah ada tidak diduplikasi.

Jalankan:  python seed.py   (atau: make seed)
"""

from __future__ import annotations

from app.core.database import SessionLocal
from app.models import AdminAccount, Candidate, ElectionSession, Position, User
from app.services.mock_helpers import (
    ensure_default_admins,
    ensure_default_election_data,
    ensure_default_voters,
)


def run() -> None:
    db = SessionLocal()
    try:
        session = ensure_default_election_data(db)
        ensure_default_voters(db)
        ensure_default_admins(db)

        users = db.query(User).count()
        admins = db.query(AdminAccount).count()
        positions = db.query(Position).count()
        candidates = db.query(Candidate).count()
        sessions = db.query(ElectionSession).count()

        print("Seed selesai:")
        print(f"  Sesi pemilihan : {sessions} (aktif: {session.name})")
        print(f"  Jabatan        : {positions}")
        print(f"  Kandidat       : {candidates}")
        print(f"  Mahasiswa (DPT): {users}  (password default: 'password')")
        print(f"  Admin/panitia  : {admins}  (mis. panitia1 / PanitiaIT123!)")
    finally:
        db.close()


if __name__ == "__main__":
    run()
