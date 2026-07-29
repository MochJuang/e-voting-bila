# Panduan Screenshot BAB IV

Checklist tangkapan layar (SS-01 s/d SS-26) yang perlu dimasukkan ke BAB IV.
Penanda `📸 [SS-xx]` sudah ditempatkan pada posisi yang sesuai di `BAB4_Hasil_dan_Pembahasan.md`.

## Persiapan (nyalakan sistem lebih dulu)

```bash
# 1) Database
docker compose up -d mysql

# 2) Backend (terminal terpisah)
cd backend && make setup && make start        # migrasi + seed + jalankan API di :8000

# 3) Frontend (terminal terpisah)
cd mockup && npm run dev                       # buka URL yang tampil (mis. http://localhost:5173)
```

Akun uji: mahasiswa `2141721001` (password `password`) · panitia `panitia1` (password `PanitiaIT123!`).

## A. Antarmuka & Implementasi (§4.2)

| Kode | Apa yang di-capture | Sumber |
|---|---|---|
| SS-01 | Halaman beranda | `/` |
| SS-02 | Login mahasiswa | `/login` |
| SS-03 | Dashboard mahasiswa | `/dashboard` |
| SS-04 | Login panitia | `/admin/login` |
| SS-05 | Dashboard panitia (statistik pemilih) | `/admin/dashboard` |
| SS-06 | Pengelolaan kandidat | `/admin/kandidat` |
| SS-07 | Pengelolaan mahasiswa (status wajah/voting/kunci) | `/admin/mahasiswa` |
| SS-08 | Rekapitulasi hasil | `/admin/rekapitulasi` |
| SS-09 | Kiosk admin-assisted (input NIM) | `/admin/kiosk` |
| SS-10 | Halaman "sudah memilih" / selesai | `/selesai` atau `/sudah-memilih` |
| SS-11 | Struktur tabel basis data | Adminer http://localhost:8080 (server `mysql`, user `root`, password kosong) |
| SS-12 | Registrasi wajah — pemindaian 5 pose | `/registrasi-wajah` |
| SS-13 | Verifikasi wajah realtime (bar similarity) | `/verifikasi-wajah` |
| SS-14 | Banner tantangan liveness (senyum/hadap kiri/hadap kanan) | `/verifikasi-wajah` (setelah wajah cocok) |
| SS-15 | Booth voting (daftar kandidat) | `/booth` |

## B. Pengujian (§4.3)

Jalankan pada folder `backend` (aktifkan virtualenv bila perlu: `source .venv/bin/activate`).

| Kode | Apa yang di-capture | Perintah |
|---|---|---|
| SS-16 | Seluruh test PASSED (40 test) | `pytest -v` |
| SS-17 | Build frontend berhasil | `cd mockup && npm run build` |
| SS-18 | Validasi model InsightFace (similarity 1,00; 5/5 pose) | jalankan skrip validasi biometrik (lihat di bawah) |
| SS-19 | Modul Autentikasi | `pytest tests/test_modul_autentikasi.py -v` |
| SS-20 | Modul Registrasi Wajah | `pytest tests/test_modul_registrasi_wajah.py -v` |
| SS-21 | Modul Verifikasi & Liveness | `pytest tests/test_modul_verifikasi_liveness.py -v` |
| SS-22 | Modul Pemungutan Suara | `pytest tests/test_modul_voting.py -v` |
| SS-23 | Modul Panitia/Admin | `pytest tests/test_modul_admin.py -v` |
| SS-24 | Modul Keamanan | `pytest tests/test_modul_keamanan.py -v` |
| SS-25 | Modul Face Service (unit algoritma) | `pytest tests/test_face_service.py -v` |
| SS-26 | Alur realtime di browser (2–3 tangkapan berurutan) | demo `/verifikasi-wajah` → `/booth` |

### Catatan SS-18 / Gambar 4.22 (validasi model InsightFace)

Jalankan skrip `backend/validate_insightface.py` yang menjalankan pipeline pada
**model InsightFace asli** (bukan mode fallback test). Run pertama mengunduh
`buffalo_l` (±280 MB, butuh internet).

```bash
# di folder backend, dengan venv aktif
python validate_insightface.py                 # pakai gambar contoh bawaan InsightFace
python validate_insightface.py wajah.jpg       # ATAU pakai foto wajah sendiri (1 wajah)
python validate_insightface.py wajah.jpg orang_lain.jpg   # + uji penolakan wajah berbeda
```

Keluaran yang di-screenshot menampilkan: mode model (InsightFace ASLI), 1 wajah
terdeteksi, sinyal biometrik (yaw/pitch/ear/smile), **5/5 pose diterima**,
**similarity 1,000 → COCOK**, dan tantangan liveness menolak wajah statis.
