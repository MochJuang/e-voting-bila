# PRD: E-Voting Ketua Himpunan Mahasiswa Teknik Informatika Nusa Putra

## 1. Latar Belakang

Pemilihan Ketua Himpunan Mahasiswa Teknik Informatika (HMTI) Universitas Nusa Putra saat ini rawan masalah: satu mahasiswa memilih lebih dari sekali, kandidat/pemilih tidak terverifikasi identitasnya, dan rekapitulasi manual yang lambat serta rawan salah hitung. Sistem E-Voting Ketua HMTI Nusa Putra adalah aplikasi web e-voting yang menggunakan **NIM + password** sebagai kredensial dasar dan **verifikasi wajah + liveness detection** sebagai lapisan anti-kecurangan, untuk memastikan satu mahasiswa = satu suara, dan yang memilih adalah orang yang bersangkutan (bukan diwakilkan).

## 2. Tujuan

- Menyediakan proses pemilihan digital yang **aman** (anti double-voting, anti-impersonation) dan **auditable**.
- Mendukung pemilihan **multi-jabatan** dalam satu sesi voting (mis. Ketua, Wakil Ketua, Senator, dll — pemilih menyelesaikan seluruh jabatan sebelum suara disimpan final).
- Memberikan hasil rekapitulasi yang cepat dan akurat setelah masa pemilihan ditutup.

## 3. Target Pengguna

| Role | Deskripsi |
|---|---|
| **Mahasiswa Pemilih** | Mendaftar, registrasi wajah, login, verifikasi, dan memberikan suara untuk setiap jabatan yang dibuka. |
| **Admin/Panitia Pemilihan** | Mengelola data kandidat per jabatan, membuka/menutup masa pendaftaran & pemungutan suara, memantau proses, mengunduh rekapitulasi hasil. |
| **Super Admin (opsional)** | Mengelola akun admin/panitia, konfigurasi sistem, audit log. |

## 4. Ruang Lingkup

### 4.1 In Scope
- Web app responsive (bisa diakses browser laptop maupun tablet/HP di booth pemungutan suara).
- Pendaftaran akun mahasiswa + registrasi wajah (enrollment).
- Login (NIM & password) + verifikasi wajah & liveness sebagai second factor sebelum masuk ke booth voting.
- Pemungutan suara untuk **banyak jabatan sekaligus** dalam satu sesi.
- Pencegahan pemilihan ganda (per jabatan & per sesi).
- Rekapitulasi hasil per jabatan setelah masa pemilihan ditutup.
- Panel admin untuk kelola kandidat, jadwal, dan monitoring.

### 4.2 Out of Scope (v1)
- Aplikasi mobile native (bisa jadi fase berikutnya).
- Verifikasi wajah untuk kandidat (hanya untuk pemilih).
- Integrasi dengan sistem akademik kampus (SIAKAD) untuk sinkronisasi NIM otomatis — di v1, data mahasiswa diimpor manual/CSV oleh admin.
- E-voting untuk pemilihan di luar lingkup organisasi kampus (mis. pemilu nasional).

## 5. Mode Akses Mahasiswa

Setiap mahasiswa di DPT memiliki flag akses (diset oleh admin saat impor data atau kapan pun sebelum voting), yang menentukan jalur masuk mahasiswa tersebut ke sistem:

| Flag | Nilai | Jalur Masuk | Kapan Dipakai |
|---|---|---|---|
| `mode_akses = mandiri` (flag unrestricted **OFF**) | Standar | Mahasiswa login sendiri di device apa pun dengan **NIM & password miliknya**, lalu lanjut verifikasi wajah & liveness, lalu pilih kandidat. | Mahasiswa dengan akun & data lengkap (kasus umum). |
| `mode_akses = admin_assisted` (flag unrestricted **ON**) | Terbantu Admin | Proses **wajib** dilakukan di **komputer kiosk khusus** (1–2 unit yang disiapkan panitia untuk sesi pemilihan). Panitia login ke **akun admin** di komputer tersebut. Di dalam sesi admin itu, mahasiswa memasukkan **NIM miliknya sendiri**, lalu tetap melalui **verifikasi wajah & liveness sendiri**, lalu **memilih kandidat sendiri**. | Mahasiswa yang belum punya password/akun lengkap, lupa password, atau datanya belum sepenuhnya terverifikasi — sehingga tidak bisa lolos login mandiri, tapi identitasnya tetap divalidasi via NIM + biometrik saat itu juga. |

Poin penting: **mode admin-assisted bukan proxy voting.** Admin tidak memilih atas nama mahasiswa — admin hanya menyediakan konteks sesi yang terotentikasi (menggantikan langkah login password), sementara input NIM, verifikasi wajah/liveness, dan pemilihan kandidat tetap dilakukan langsung oleh mahasiswa yang bersangkutan. Ini menjaga agar kontrol anti-kecurangan (satu wajah = satu suara) tetap berlaku di kedua mode.

### Implikasi Keamanan
- Komputer kiosk untuk mode admin-assisted harus **didaftarkan/whitelist** (device ID atau IP tertentu) — sistem menolak memulai sesi admin-assisted dari device yang tidak terdaftar, supaya jalur ini tidak disalahgunakan dari sembarang komputer.
- Setiap sesi admin-assisted dicatat di audit log: admin mana yang login, device mana, NIM mahasiswa yang dibantu, dan timestamp — untuk akuntabilitas karena jalur ini melewati langkah password.
- Setelah satu mahasiswa selesai vote di kiosk, sesi harus otomatis kembali ke layar "masukkan NIM" berikutnya (bukan tetap dalam sesi mahasiswa sebelumnya) agar admin tidak perlu logout-login berulang tapi tetap tidak bocor ke mahasiswa berikutnya.
- Status "sudah memilih" & pengecekan double-voting (kode I/X di alur) berlaku sama persis di kedua mode — pengecekan dilakukan berdasarkan identitas mahasiswa (NIM), bukan berdasarkan jalur akses yang dipakai.

## 6. Alur Proses (mengacu ke Diagram Rules)

### Tahap 1 — Pendaftaran
| Kode | Langkah | Detail |
|---|---|---|
| A | Daftar (Mahasiswa Pemilih) | Mahasiswa membuat akun dengan NIM, nama, email kampus, dan password. |
| B | Login (NIM & Password) | Autentikasi kredensial dasar. |
| D | Registrasi & Verifikasi Wajah | Mahasiswa mengambil foto wajah (enrollment) via webcam/kamera device. Sistem mengekstrak face embedding dan menyimpannya terenkripsi. |
| F | Verifikasi Wajah & Liveness | Sistem memvalidasi bahwa wajah yang di-capture adalah wajah hidup (bukan foto/video/print), lalu mencocokkan dengan wajah yang sudah didaftarkan. |
| C | Wajah Ada? (Ya/Tidak) | Jika sistem gagal mendeteksi wajah pada frame → kembali ke langkah D (ambil ulang foto). Jika wajah terdeteksi → lanjut ke Tahap 2. |

### Tahap 2 — Verifikasi
| Kode | Langkah | Detail |
|---|---|---|
| F | Verifikasi Wajah & Liveness | Dilakukan ulang setiap kali mahasiswa akan memasuki sesi pemungutan suara (bukan hanya saat registrasi), untuk memastikan yang login = yang memilih. |
| G | Valid? (Ya/Tidak) | Jika kecocokan wajah (face match score) di bawah threshold, atau liveness check gagal → kembali ke F (retry, dengan batas maksimal percobaan, mis. 3x sebelum akun di-lock sementara dan perlu verifikasi manual oleh panitia). Jika valid → lanjut ke Tahap 3. |

### Tahap 3 — Pemungutan Suara
| Kode | Langkah | Detail |
|---|---|---|
| I | Sudah Memilih? (Ya/Tidak) | Sistem mengecek status voting mahasiswa untuk sesi pemilihan aktif. |
| X | Sudah Memilih, Akses Ditolak | Jika mahasiswa sudah menyelesaikan seluruh pemungutan suara pada sesi ini, akses ke booth ditolak dan diarahkan ke halaman status akhir. |
| K | Masuk Booth | Jika belum memilih, mahasiswa masuk ke tampilan booth digital (surat suara digital). |
| L | Pilih Kandidat | Untuk **setiap jabatan yang dibuka**, mahasiswa memilih satu kandidat/paslon. Sistem memvalidasi seluruh jabatan telah diisi sebelum submit final diperbolehkan. Setelah submit, sistem re-check status "Sudah Memilih?" (I) untuk mencegah submit ganda dari race condition (mis. dua tab terbuka) — jika sudah tersimpan, diarahkan ke X. |

### Tahap 4 — Penutupan
| Kode | Langkah | Detail |
|---|---|---|
| M & N | Simpan & Update Status | Suara disimpan (dengan enkripsi/anonimisasi agar suara tidak bisa ditelusuri balik ke identitas pemilih), status "sudah memilih" mahasiswa diupdate. |
| O | Rekapitulasi Hasil | Setelah masa pemilihan ditutup oleh admin, sistem menghitung total suara per kandidat per jabatan dan menampilkan hasil resmi. |

## 7. Functional Requirements

### 7.1 Manajemen Akun & Registrasi
- FR-1: Mahasiswa dapat mendaftar dengan NIM unik + password (hash, bukan plaintext).
- FR-2: Admin dapat mengimpor daftar NIM mahasiswa yang berhak memilih (whitelist) via CSV, agar pendaftaran hanya bisa dilakukan oleh mahasiswa yang terdaftar dalam DPT (Daftar Pemilih Tetap). Saat impor, admin dapat menandai `mode_akses` tiap mahasiswa (`mandiri` / `admin_assisted`); default `mandiri` kecuali ditandai lain.
- FR-3: Proses enrollment wajah wajib dilakukan sebelum akun bisa digunakan untuk memilih; minimal 1 foto referensi berkualitas baik (deteksi pencahayaan/blur/sudut wajah). Berlaku untuk kedua mode akses.
- FR-4: Sistem memberi feedback real-time saat capture wajah gagal (tidak ada wajah, terlalu gelap, wajah ganda dalam frame, dll — kode C: "Wajah Ada?").

### 7.2 Autentikasi & Verifikasi
- FR-5: Login dua langkah untuk mode `mandiri`: (1) NIM & password, (2) verifikasi wajah + liveness sebelum akses ke booth.
- FR-5a: Untuk mode `admin_assisted`, jalur masuk adalah: admin login ke akun admin di kiosk terdaftar → mahasiswa input NIM sendiri (sistem memvalidasi NIM tsb memang berstatus `admin_assisted`, jika tidak maka arahkan ke jalur mandiri) → verifikasi wajah & liveness mahasiswa sendiri → lanjut booth. Tidak ada input password mahasiswa di jalur ini.
- FR-6: Liveness detection harus menolak foto statis, video replay, dan deepfake sederhana (spoofing dasar) — berlaku di kedua mode akses.
- FR-7: Threshold kecocokan wajah dan jumlah percobaan maksimum dapat dikonfigurasi oleh admin.
- FR-8: Setelah gagal verifikasi melebihi batas percobaan, akun di-flag untuk verifikasi manual oleh panitia (mis. tatap muka) sebelum dibuka kembali.
- FR-8a: Sistem menolak memulai sesi `admin_assisted` dari device yang tidak terdaftar sebagai kiosk resmi (lihat §5 Implikasi Keamanan).
- FR-8b: Setelah satu sesi voting `admin_assisted` selesai (submit sukses/gagal/dibatalkan), sistem otomatis kembali ke layar input NIM berikutnya tanpa mengekspos data mahasiswa sebelumnya.

### 7.3 Pemungutan Suara
- FR-9: Sistem mendukung konfigurasi banyak jabatan dalam satu sesi pemilihan, masing-masing dengan daftar kandidat/paslon sendiri (termasuk opsi "kandidat kosong/abstain" bila diatur panitia).
- FR-10: Mahasiswa harus memberikan suara pada seluruh jabatan yang wajib diisi sebelum submit final diterima (all-or-nothing per sesi).
- FR-11: Setelah submit, status voting mahasiswa dikunci permanen untuk sesi tersebut — tidak bisa vote ulang atau mengubah pilihan, terlepas dari mode akses yang dipakai.
- FR-12: Sistem harus menangani race condition (submit ganda dari device/tab berbeda) — hanya submit pertama yang valid.

### 7.4 Admin & Rekapitulasi
- FR-13: Admin dapat membuat/mengedit sesi pemilihan, jabatan, dan kandidat (nama, foto, visi-misi, nomor urut).
- FR-14: Admin dapat membuka dan menutup masa pendaftaran dan masa pemungutan suara (jadwal otomatis + override manual).
- FR-15: Admin dapat memonitor jumlah pemilih yang sudah/belum memilih secara real-time (tanpa melihat pilihan individu — hanya status "sudah/belum").
- FR-16: Setelah sesi ditutup, sistem menghasilkan rekapitulasi hasil per jabatan (jumlah suara per kandidat, persentase partisipasi) yang dapat diekspor (PDF/Excel).
- FR-17: Sistem mencatat audit log untuk aksi admin (buka/tutup sesi, edit kandidat, dsb).
- FR-18: Admin dapat mendaftarkan/menghapus device sebagai kiosk resmi untuk mode `admin_assisted`, dan mengubah `mode_akses` mahasiswa individual kapan pun sebelum mahasiswa tsb memilih.
- FR-19: Admin dapat melihat log seluruh sesi `admin_assisted` (admin yang login, device, NIM yang dibantu, waktu) sebagai bagian dari audit trail.

## 8. Non-Functional Requirements

- **Keamanan**
  - Data biometrik (face embedding) disimpan terenkripsi at-rest, tidak disimpan sebagai foto mentah kecuali diperlukan untuk audit terbatas.
  - Suara pemilih disimpan anonim/ter-dekopel dari identitas mahasiswa (mis. gunakan token voting terpisah dari record identitas) untuk menjamin kerahasiaan pilihan (secrecy of ballot) sekaligus mencegah double voting.
  - Password di-hash (bcrypt/argon2). Rate limiting pada endpoint login & verifikasi wajah untuk mencegah brute force.
  - HTTPS wajib di seluruh endpoint; sesi login menggunakan token dengan masa berlaku pendek.
- **Privasi & Kepatuhan**
  - Perlu persetujuan eksplisit (consent) dari mahasiswa saat enrollment wajah, sesuai UU PDP (data biometrik = data pribadi spesifik).
  - Kebijakan retensi: data wajah dihapus setelah periode tertentu pasca pemilihan berakhir (mis. sesuai kebijakan kampus, didiskusikan dengan panitia).
- **Performa**
  - Verifikasi wajah (face match + liveness) harus selesai < 3 detik per percobaan agar tidak menimbulkan antrian panjang di booth.
  - Sistem harus tetap responsif untuk beban puncak (skala kampus kecil, <5.000 pemilih, dengan asumsi burst traffic saat jam pembukaan booth).
- **Ketersediaan**
  - Uptime tinggi selama jendela waktu pemungutan suara (mis. 99.5% selama masa aktif voting); perlu monitoring & alerting.
- **Auditability**
  - Seluruh transisi status (registrasi, verifikasi, submit suara, penutupan sesi) tercatat di audit log dengan timestamp.

## 9. Pertimbangan Teknis — Verifikasi Wajah & Liveness

Berdasarkan diskusi, pendekatan yang direkomendasikan:

- **Face recognition**: InsightFace (model ArcFace) untuk ekstraksi embedding wajah — open-source, akurasi tinggi, self-hosted (data tidak dikirim ke pihak ketiga).
- **Capture & preprocessing**: OpenCV untuk capture kamera, deteksi wajah awal (bounding box), alignment, dan quality check (blur, pencahayaan, sudut).
- **Liveness detection**: OpenCV saja tidak cukup untuk anti-spoofing yang andal. Dua opsi:
  - **Passive liveness (direkomendasikan untuk UX lebih cepat)**: model open-source seperti *Silent-Face-Anti-Spoofing*, berjalan dari satu frame/beberapa frame tanpa perlu instruksi ke user.
  - **Active liveness (fallback/tambahan keamanan)**: challenge-response (mis. "kedipkan mata" / "geleng kepala") menggunakan facial landmark detection (MediaPipe/dlib) — lebih lambat tapi lebih tahan terhadap serangan canggih (mis. video replay resolusi tinggi).
  - Rekomendasi: mulai dengan passive liveness untuk kecepatan; tambahkan active liveness sebagai lapisan kedua jika threshold passive liveness meragukan (di area abu-abu antara jelas asli vs jelas palsu).
- **Deployment**: proses face matching & liveness sebaiknya dijalankan di server (bukan di browser client) untuk mencegah manipulasi hasil verifikasi oleh client; browser hanya mengirim frame/video pendek terenkripsi ke backend.
- **Infrastruktur**: karena skala kecil (<5.000 pemilih), GPU tidak wajib — InsightFace + Silent-Face-Anti-Spoofing bisa berjalan cukup baik di CPU untuk throughput ini, namun perlu load-test di jam sibuk booth.

## 10. Model Data (Ringkas)

- **User** (mahasiswa): id, NIM, nama, email, password_hash (nullable jika `mode_akses = admin_assisted` dan belum pernah set password), face_embedding_ref, status_verifikasi, dpt_status, `mode_akses` (enum: `mandiri` | `admin_assisted`)
- **AdminAccount**: id, username, password_hash, role
- **KioskDevice**: id, nama_lokasi, device_id/IP terdaftar, status_aktif — daftar device yang diizinkan menjalankan sesi `admin_assisted`
- **Session Pemilihan**: id, nama_sesi, jadwal_daftar_mulai/selesai, jadwal_voting_mulai/selesai, status
- **Jabatan**: id, session_id, nama_jabatan, wajib_diisi
- **Kandidat**: id, jabatan_id, nama, nomor_urut, foto, visi_misi
- **VotingRecord** (anonim): id, session_id, jabatan_id, candidate_id, voting_token (bukan langsung user_id), timestamp
- **VoterStatus**: user_id, session_id, has_voted (boolean) — terpisah dari VotingRecord untuk menjaga kerahasiaan pilihan
- **AssistedSessionLog**: id, admin_id, kiosk_device_id, user_id (NIM yang dibantu), timestamp_mulai, timestamp_selesai, hasil (sukses/gagal/dibatalkan)
- **AuditLog**: id, actor_id, action, target, timestamp

## 11. Edge Cases & Error Handling

- Wajah tidak terdeteksi berulang kali → arahkan ke bantuan panitia/verifikasi manual, jangan biarkan user terjebak loop tanpa jalan keluar.
- Koneksi terputus saat submit suara di tengah proses → perlu idempotency key agar tidak tercatat ganda saat retry, dan status jelas ke user (berhasil/gagal, bukan ambigu).
- Mahasiswa dengan disabilitas visual/motorik yang kesulitan proses capture wajah → sediakan jalur verifikasi manual berbasis KTM/KTP oleh panitia sebagai fallback aksesibilitas.
- Dua device/tab dibuka bersamaan oleh mahasiswa yang sama → hanya satu submit yang valid, harus ada locking di level database (unique constraint pada VoterStatus per session).
- Pencahayaan booth buruk → beri panduan UI (indikator kualitas capture) sebelum submit foto.
- Mahasiswa `admin_assisted` mencoba mengakses jalur mandiri (login NIM+password) dari device biasa tanpa punya password → sistem harus menolak dengan pesan jelas ("hubungi panitia di lokasi kiosk"), bukan error generik.
- Kiosk admin lupa logout/di-idle terlalu lama antar mahasiswa → sistem auto-timeout sesi admin_assisted per-mahasiswa setelah durasi tertentu tanpa aktivitas, kembali ke layar input NIM.

## 12. Metrik Keberhasilan

- **Partisipasi**: % mahasiswa dalam DPT yang berhasil menyelesaikan voting (dipecah juga per mode akses, mandiri vs admin_assisted, untuk evaluasi beban kiosk).
- **Tingkat penolakan verifikasi wajah palsu ditolak (spoof rejection rate)** vs **false rejection rate** pemilih sah — target false rejection rendah agar tidak menghalangi pemilih sah.
- **Waktu rata-rata per pemilih** dari login hingga submit selesai (target UX: < 2 menit termasuk verifikasi wajah).
- **Zero double-voting**: 0 kasus suara ganda tervalidasi setelah audit.
- **Downtime selama masa voting**: mendekati 0.
- **Antrian kiosk admin_assisted**: rata-rata waktu tunggu mahasiswa di kiosk tidak menjadi bottleneck (dipantau khusus karena hanya 1-2 unit device).

## 13. Open Questions

1. Apakah dibutuhkan integrasi dengan SIAKAD/sistem akademik untuk data DPT, atau cukup impor manual CSV oleh panitia?
2. Bagaimana kebijakan retensi data wajah pasca pemilihan (dihapus setelah berapa lama)?
3. Apakah dibutuhkan mode offline/degradasi jika verifikasi wajah server down saat hari-H (mis. fallback ke verifikasi manual panitia)?
4. Apakah booth voting mode mandiri akan menggunakan device bersama (tablet/PC di lokasi fisik) atau mahasiswa bisa vote dari device pribadi masing-masing (mempengaruhi desain UX & keamanan kamera)?
5. Berapa jumlah maksimum jabatan yang perlu didukung dalam satu sesi, untuk estimasi kompleksitas UI surat suara digital?
6. Berapa perkiraan jumlah mahasiswa yang akan berstatus `admin_assisted` — apakah 1-2 kiosk device cukup untuk menghindari antrian panjang di hari-H?
7. Siapa yang berwenang mengubah `mode_akses` mahasiswa dari `mandiri` ke `admin_assisted` (atau sebaliknya) di hari-H, dan apakah perlu approval berlapis mengingat ini melewati kontrol password?
