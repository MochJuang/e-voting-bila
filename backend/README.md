# Backend Structure

FastAPI backend for the e-voting mockup.

## Goals

- Use MySQL as the primary database.
- Support face enrollment and verification with InsightFace.
- Match the frontend mockup flow and route names.

## Proposed Layout

```text
backend/
  app/
    api/
      v1/
        endpoints/
    core/
    crud/
    db/
    models/
    schemas/
    services/
    utils/
    main.py
  alembic/
  tests/
  .env.example
  requirements.txt
```

## Notes

- `models/` holds SQLAlchemy models.
- `schemas/` holds Pydantic request/response contracts.
- `services/` holds business logic such as face verification.
- `api/v1/endpoints/` holds route handlers grouped by feature.
- `db/` holds database session and base model wiring.
- `alembic/` is reserved for migrations.

## Menjalankan (Development)

1. **Jalankan MySQL via Docker** (dari root repo — login `root`, password kosong, db `e_voting`):

   ```bash
   docker compose up -d mysql
   ```

   Opsional Adminer (UI DB) di http://localhost:8080 — server `mysql`, user `root`, password dikosongkan.

2. **Siapkan environment & dependensi backend:**

   ```bash
   cd backend
   cp .env.example .env   # sudah menunjuk ke root@127.0.0.1 tanpa password
   pip install -r requirements.txt
   ```

3. **Migrasi skema & seed data awal:**

   ```bash
   make setup   # = alembic upgrade head + python seed.py
   ```

   Atau terpisah: `make migrate` lalu `make seed`. Seed bersifat idempotent
   (aman dijalankan berulang) dan mengisi: 1 sesi pemilihan aktif, 1 jabatan,
   3 kandidat, 8 mahasiswa DPT (password default `password`), dan 2 admin
   (`panitia1` / `panitia2`, password `PanitiaIT123!`).

4. **Jalankan API:**

   ```bash
   make start   # uvicorn app.main:app --reload di :8000
   ```

## Verifikasi Wajah & Liveness (alur baru)

- **Enrollment (`POST /face/enroll`)** memindai **5 pose** (`center`, `up`, `right`, `down`, `left`).
  Body: `{ "nim": "...", "frames": [{ "pose": "center", "image_base64": "..." }, ...] }`.
  Semua embedding pose disimpan (dikemas dalam satu kolom `face_profiles.embedding`, format `.npy`).
- **Verifikasi (`POST /face/verify`)** bersifat realtime dan bertahap (`stage`):
  - `stage=match`: frontend mengirim frame secara streaming; backend membandingkan embedding.
    Saat cocok, backend mengembalikan `matched=true` + `challenge` acak
    (`smile` / `turn_left` / `turn_right`).
  - `stage=liveness`: backend memeriksa gerakan sesuai challenge (senyum/menoleh) dari
    pose & landmark InsightFace; jika lolos → `verification_token` diterbitkan.
  - `timed_out=true`: dicatat sebagai percobaan gagal (untuk statistik/audit); tidak ada batas
    jumlah percobaan — mahasiswa boleh mengulang verifikasi tanpa batas hingga berhasil.
- Jika model InsightFace tidak tersedia di runtime, service otomatis memakai **mode fallback**
  (embedding berbasis hash + liveness disimulasikan) sehingga alur tetap dapat didemokan.
- Ambang batas dapat dikonfigurasi di `.env` / `config.py`:
  `FACE_MATCH_THRESHOLD`, `LIVENESS_YAW_THRESHOLD`,
  `LIVENESS_SMILE_THRESHOLD`, `ENROLL_ENFORCE_POSE_DIRECTION`.

