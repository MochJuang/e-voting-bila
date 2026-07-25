# Pengujian (Unit & Integration Test)

Test ditulis dengan **pytest** dan dijalankan pada database **SQLite in-memory**
(terisolasi, tidak menyentuh MySQL). Modul wajah diuji pada **mode fallback**
sehingga cepat dan deterministik tanpa perlu mengunduh model InsightFace.

## Menjalankan

```bash
cd backend
pip install -r requirements-dev.txt   # sekali saja (pytest + httpx)
pytest -v
```

## Struktur test per modul (untuk BAB IV §4.3)

Setiap file test = satu modul pengujian, setiap fungsi = satu test case
(bisa di-*screenshot* per modul).

| File test | Modul (§4.3.x) | Jumlah test |
|---|---|---|
| `test_modul_autentikasi.py` | Autentikasi (registrasi, login, reset password) | 7 |
| `test_modul_registrasi_wajah.py` | Registrasi Wajah (enrollment 5 pose) | 4 |
| `test_modul_verifikasi_liveness.py` | Verifikasi Wajah & Liveness (realtime) | 5 |
| `test_modul_voting.py` | Pemungutan Suara (booth & anti suara ganda) | 5 |
| `test_modul_admin.py` | Panitia/Admin (login, dashboard) | 4 |
| `test_modul_keamanan.py` | Keamanan (proteksi akses, hashing, isolasi NIM) | 4 |
| `test_face_service.py` | Face Service (unit algoritma inti) | 11 |
| **Total** | | **40** |

## Tips screenshot

- Per modul: `pytest tests/test_modul_autentikasi.py -v`
- Semua sekaligus: `pytest -v`
- Ringkas (hanya hasil akhir): `pytest -q`
