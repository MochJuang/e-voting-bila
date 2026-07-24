from __future__ import annotations

from dataclasses import dataclass, field

from app.models.enums import AccessMode, SessionStatus


@dataclass(frozen=True)
class MockCandidate:
    id: int
    nama: str
    nomor: int
    warna: str
    visi: str


@dataclass(frozen=True)
class MockPosition:
    id: str
    nama: str
    kandidat: list[MockCandidate] = field(default_factory=list)


@dataclass(frozen=True)
class MockVoter:
    nim: str
    nama: str
    kelas: str
    mode_akses: AccessMode
    has_voted: bool
    face_enrolled: bool


@dataclass(frozen=True)
class MockAdmin:
    username: str
    password: str
    role: str = "admin"


DEFAULT_POSITIONS = [
    MockPosition(
        id="ketua",
        nama="Ketua Himpunan IT",
        kandidat=[
            MockCandidate(1, "Adit Pratama", 1, "#2563eb", "Program kerja terukur untuk mahasiswa IT."),
            MockCandidate(2, "Nabila Putri", 2, "#9333ea", "Kolaborasi lintas angkatan dan prodi."),
            MockCandidate(3, "Rizky Ramadhan", 3, "#ea580c", "Digitalisasi layanan himpunan."),
        ],
    ),
]

DEFAULT_VOTERS = [
    MockVoter("2141721001", "Ahmad Fauzan", "TI-3A", AccessMode.MANDIRI, False, True),
    MockVoter("2141721002", "Siti Nurhaliza", "TI-3B", AccessMode.MANDIRI, True, True),
    MockVoter("2141721003", "Budi Santoso", "SI-3A", AccessMode.ADMIN_ASSISTED, False, True),
    MockVoter("2141721004", "Putri Wulandari", "SI-2B", AccessMode.ADMIN_ASSISTED, False, False),
    MockVoter("2141721005", "Reza Firmansyah", "TI-2A", AccessMode.MANDIRI, False, False),
    MockVoter("2141721006", "Dewi Lestari", "DKV-2A", AccessMode.MANDIRI, False, True),
    MockVoter("2141721007", "Farhan Maulana", "TI-1B", AccessMode.ADMIN_ASSISTED, False, False),
    MockVoter("2141721008", "Larasati Putri", "SI-1A", AccessMode.MANDIRI, True, True),
]

DEFAULT_ADMINS = [
    MockAdmin("panitia1", "PanitiaIT123!"),
    MockAdmin("panitia2", "PanitiaIT123!"),
]

DEFAULT_SESSION = {
    "id": 1,
    "name": "Pemilihan Ketua Himpunan IT 2026",
    "status": SessionStatus.VOTING_OPEN,
    "registration_open_at": None,
    "registration_close_at": None,
    "voting_open_at": None,
    "voting_close_at": None,
    "description": "Sesi aktif mockup pemilihan ketua himpunan IT",
}
