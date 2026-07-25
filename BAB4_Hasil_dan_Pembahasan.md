# BAB IV

## HASIL DAN PEMBAHASAN

### 4.1 Gambaran Umum Implementasi

Hasil penelitian ini berupa sistem *e-voting* berbasis web untuk pemilihan Ketua Himpunan Mahasiswa Teknik Informatika. Sistem dibangun dengan arsitektur *client-server* menggunakan *frontend* React JS dan *backend* FastAPI, dengan penyimpanan data pada basis data relasional MySQL. Sistem tidak hanya menyediakan proses login dan pemungutan suara, tetapi juga mendukung registrasi wajah, verifikasi wajah berbasis *face embedding*, serta *liveness detection* secara *realtime* untuk meningkatkan keamanan autentikasi pemilih.

Secara fungsional, sistem dibagi menjadi dua peran utama, yaitu mahasiswa sebagai pemilih dan panitia sebagai pengelola sistem. Mahasiswa dapat melakukan pendaftaran akun, registrasi wajah, login, verifikasi identitas, dan pemberian suara. Panitia dapat mengelola data mahasiswa, kandidat, sesi pemilihan, dan melihat rekapitulasi hasil voting.

Alur implementasi sistem mengikuti rancangan pada BAB III, yaitu:

1. Mahasiswa login menggunakan NIM dan password.
2. Sistem memverifikasi wajah secara *realtime* dengan beberapa *frame* kamera.
3. Jika wajah sesuai, sistem menampilkan satu tantangan *liveness* acak secara otomatis.
4. Setelah *liveness* berhasil, mahasiswa diarahkan ke halaman *booth* voting.
5. Suara disimpan ke basis data dan status pemilih diperbarui menjadi sudah memilih.

```mermaid
flowchart LR
    A["Mahasiswa / Panitia"] --> B["Frontend React JS"]
    B --> C["API FastAPI"]
    C --> D["MySQL"]
    C --> E["Face Service"]
    E --> F["InsightFace (embedding & landmark)"]
    E --> G["OpenCV (praproses citra)"]
    D --> H["Data Pemilih, Kandidat, Voting, dan Log"]
```

Keterangan Gambar 4.1 Arsitektur Implementasi Sistem

### 4.2 Hasil Implementasi Sistem

#### 4.2.1 Antarmuka Pengguna

Antarmuka pengguna dibangun menggunakan React JS dan Vite agar tampilan responsif dan mudah digunakan. Halaman utama yang tersedia pada sistem meliputi:

1. Halaman beranda.
2. Halaman daftar akun mahasiswa.
3. Halaman login mahasiswa.
4. Halaman reset password mahasiswa.
5. Halaman dashboard mahasiswa.
6. Halaman registrasi wajah.
7. Halaman verifikasi wajah dan *liveness*.
8. Halaman *booth* voting.
9. Halaman status sudah memilih.
10. Halaman selesai.
11. Halaman login panitia.
12. Halaman dashboard panitia.
13. Halaman kiosk mode bantuan panitia (*admin-assisted*).
14. Halaman pengelolaan kandidat.
15. Halaman pengelolaan mahasiswa.
16. Halaman rekapitulasi hasil.

Struktur halaman tersebut memisahkan fungsi mahasiswa dan panitia sehingga alur penggunaan sistem menjadi lebih jelas.

**Tangkapan layar antarmuka yang perlu disisipkan:**

- 📸 **[SS-01]** Halaman beranda (`/`) — *Gambar 4.5 Halaman Beranda*.
- 📸 **[SS-02]** Halaman login mahasiswa (`/login`) — *Gambar 4.6 Halaman Login Mahasiswa*.
- 📸 **[SS-03]** Halaman dashboard mahasiswa (`/dashboard`) — *Gambar 4.7 Halaman Dashboard Mahasiswa*.
- 📸 **[SS-04]** Halaman login panitia (`/admin/login`) — *Gambar 4.8 Halaman Login Panitia*.
- 📸 **[SS-05]** Halaman dashboard panitia beserta statistik pemilih (`/admin/dashboard`) — *Gambar 4.9 Halaman Dashboard Panitia*.
- 📸 **[SS-06]** Halaman pengelolaan kandidat (`/admin/kandidat`) — *Gambar 4.10 Halaman Pengelolaan Kandidat*.
- 📸 **[SS-07]** Halaman pengelolaan mahasiswa — kolom status wajah, status memilih, dan akun terkunci (`/admin/mahasiswa`) — *Gambar 4.11 Halaman Pengelolaan Mahasiswa*.
- 📸 **[SS-08]** Halaman rekapitulasi hasil (`/admin/rekapitulasi`) — *Gambar 4.12 Halaman Rekapitulasi Hasil*.
- 📸 **[SS-09]** Halaman kiosk mode admin-assisted saat input NIM (`/admin/kiosk`) — *Gambar 4.13 Halaman Kiosk Mode Admin-Assisted*.
- 📸 **[SS-10]** Halaman status "sudah memilih" atau halaman selesai — *Gambar 4.14 Halaman Selesai*.

#### 4.2.2 Autentikasi Pengguna

Autentikasi pengguna pada sistem terdiri atas login mahasiswa dan login panitia. Login mahasiswa menggunakan NIM dan password, sedangkan login panitia menggunakan username dan password akun admin. Setelah login berhasil, token autentikasi disimpan untuk membatasi akses berdasarkan peran pengguna.

Pada sisi mahasiswa, login menjadi tahap awal sebelum registrasi wajah dan verifikasi biometrik dilakukan. Pada sisi panitia, autentikasi digunakan untuk membuka dashboard pengelolaan data pemilih, kandidat, dan hasil voting.

#### 4.2.3 Implementasi Basis Data

Basis data dirancang menggunakan tabel-tabel utama yang merepresentasikan entitas pada sistem *e-voting*. Tabel utama yang digunakan antara lain:

| No | Tabel | Fungsi |
|---|---|---|
| 1 | `users` | Menyimpan data mahasiswa, termasuk NIM, nama, email, password hash, mode akses, dan status pemilih. |
| 2 | `face_profiles` | Menyimpan data *face embedding* hasil registrasi wajah. |
| 3 | `election_sessions` | Menyimpan data sesi pemilihan beserta jadwal dan status. |
| 4 | `positions` | Menyimpan data jabatan yang dipilih pada sesi aktif. |
| 5 | `candidates` | Menyimpan data kandidat beserta nomor urut, visi, dan foto. |
| 6 | `votes` | Menyimpan suara yang diberikan pada setiap jabatan. |
| 7 | `voter_statuses` | Menyimpan status apakah pemilih sudah memilih pada sesi aktif. |
| 8 | `face_verification_logs` | Menyimpan log hasil verifikasi wajah dan *liveness*. |
| 9 | `kiosk_devices` | Menyimpan data perangkat kiosk untuk mode bantuan panitia. |
| 10 | `assisted_sessions` | Menyimpan riwayat sesi bantuan panitia. |

Keterangan Tabel 4.1 Implementasi Tabel Basis Data

```mermaid
erDiagram
    USERS {
        int id
        string nim
        string nama
        string email
        string password_hash
        string mode_akses
        boolean face_enrolled
        boolean has_voted
        boolean is_locked
    }
    FACE_PROFILES {
        int id
        int user_id
        binary embedding
        string embedding_version
        string image_path
        int quality_score
    }
    ELECTION_SESSIONS {
        int id
        string name
        string status
        datetime voting_open_at
        datetime voting_close_at
    }
    POSITIONS {
        int id
        int session_id
        string name
        boolean is_required
    }
    CANDIDATES {
        int id
        int position_id
        string name
        int number
        string vision
    }
    VOTES {
        int id
        int session_id
        int position_id
        int candidate_id
        string vote_token
    }

    USERS ||--o| FACE_PROFILES : memiliki
    ELECTION_SESSIONS ||--o{ POSITIONS : memiliki
    POSITIONS ||--o{ CANDIDATES : memiliki
    ELECTION_SESSIONS ||--o{ VOTES : mencatat
    POSITIONS ||--o{ VOTES : mencatat
    CANDIDATES ||--o{ VOTES : dipilih
```

Keterangan Gambar 4.2 Struktur Data Utama Sistem

> 📸 **[SS-11]** Struktur tabel basis data — tangkap daftar tabel pada Adminer (http://localhost:8080) atau MySQL, memperlihatkan tabel `users`, `face_profiles`, `candidates`, `votes`, `voter_statuses`, dan lainnya.

Keterangan Gambar 4.15 Struktur Tabel Basis Data

#### 4.2.4 Registrasi Wajah

Registrasi wajah dilakukan setelah pengguna berhasil membuat akun dan masuk ke dashboard mahasiswa. Berbeda dengan registrasi satu gambar, sistem memindai wajah pengguna dari lima sudut secara terpandu, yaitu menghadap ke tengah (lurus), atas, kanan, bawah, dan kiri. Untuk setiap pose, antarmuka memberikan instruksi arah dan hitung mundur singkat sebelum *frame* diambil, sehingga pengguna dapat memposisikan wajah dengan benar.

Setiap *frame* pose diproses oleh backend untuk mendeteksi wajah, mengukur kualitas citra (pencahayaan dan ketajaman), lalu mengekstraksi *face embedding* menggunakan InsightFace (model ArcFace *buffalo_l*). Sistem memvalidasi bahwa hanya terdapat satu wajah pada setiap *frame*; jika tidak, pose tersebut ditolak dan pengguna diminta mengulang.

Kelima embedding pose disimpan bersama pada tabel `face_profiles` dalam satu kolom biner (format array), bukan citra mentah sebagai data utama. Penyimpanan banyak sudut ini membuat proses verifikasi lebih tahan terhadap variasi posisi kepala dan pencahayaan, karena pencocokan pada tahap verifikasi dapat dibandingkan terhadap sudut yang paling mendekati.

> 📸 **[SS-12]** Halaman registrasi wajah — tangkap proses pemindaian 5 pose (`/registrasi-wajah`), tampak indikator lima pose (tengah, atas, kanan, bawah, kiri) dan panduan arah.

Keterangan Gambar 4.16 Proses Pemindaian Wajah (Registrasi 5 Pose)

#### 4.2.5 Verifikasi Wajah Secara Realtime

Verifikasi wajah dilakukan secara *realtime* dengan mengalirkan (*streaming*) *frame* kamera ke backend secara berkala, bukan melalui satu gambar statis. Pendekatan ini bertujuan memperoleh sampel wajah yang lebih representatif sehingga pencocokan identitas menjadi lebih stabil.

Alur verifikasi dimulai ketika kamera aktif dan sistem secara berkala menangkap *frame* dari webcam, lalu mengirimkannya ke backend untuk dianalisis. Backend mengekstraksi embedding dari tiap *frame* dan menghitung tingkat kemiripan (*cosine similarity*) terhadap seluruh embedding pose yang tersimpan pada profil pengguna, kemudian mengambil nilai kemiripan tertinggi. Jika nilai tersebut melebihi ambang batas yang ditentukan, maka pengguna dinyatakan cocok dan proses berlanjut secara otomatis ke tahap *liveness detection*. Selama wajah belum cocok, sistem terus memindai tanpa menghitungnya sebagai percobaan gagal, sehingga tidak memicu penguncian akun secara keliru.

```mermaid
flowchart TD
    A["Kamera aktif"] --> B["Ambil beberapa frame realtime"]
    B --> C["Ekstraksi embedding wajah"]
    C --> D["Bandingkan dengan data profil"]
    D --> E{"Wajah cocok?"}
    E -- Tidak --> F["Verifikasi ditolak"]
    E -- Ya --> G["Tampilkan challenge liveness acak"]
    G --> H["Ambil frame realtime untuk liveness"]
    H --> I{"Liveness valid?"}
    I -- Tidak --> F
    I -- Ya --> J["Akses voting diberikan"]
```

Keterangan Gambar 4.3 Alur Verifikasi Wajah dan Liveness

> 📸 **[SS-13]** Verifikasi wajah realtime — tangkap layar `/verifikasi-wajah` saat pemindaian berjalan, tampak indikator kecocokan (bar *similarity*) dan status "Memindai & mencocokkan…".

Keterangan Gambar 4.17 Proses Verifikasi Wajah Realtime

#### 4.2.6 Liveness Detection

Setelah wajah berhasil terverifikasi, sistem menampilkan satu tantangan *liveness* acak secara otomatis. Tantangan yang tersedia meliputi empat gerakan, yaitu berkedip, tersenyum, menghadap ke kiri, dan menghadap ke kanan. Tantangan dipilih secara acak oleh sistem agar proses verifikasi tidak mudah diprediksi maupun dipalsukan.

Penilaian *liveness* dilakukan di sisi backend dengan menganalisis sinyal dari hasil deteksi InsightFace pada *frame* yang dialirkan. Gerakan menghadap ke kiri atau kanan dinilai dari sudut kepala (*yaw*) hasil estimasi pose wajah, gerakan berkedip dinilai dari rasio bukaan mata (*eye aspect ratio*) yang mengecil ketika mata terpejam, dan senyum dinilai dari perubahan rasio lebar mulut terhadap jarak antar-mata. Sistem menyatakan *liveness* valid ketika *frame* yang masuk memenuhi kriteria tantangan yang diminta dalam batas waktu tertentu. Dengan mewajibkan gerakan aktif yang dipilih secara acak, sistem dapat membedakan wajah asli yang hadir langsung di depan kamera dari media tiruan seperti foto atau video yang bersifat statis.

> 📸 **[SS-14]** Tantangan liveness — tangkap saat banner tantangan acak muncul (mis. "Silakan TERSENYUM", "Silakan BERKEDIP", atau "Tolehkan kepala ke KIRI/KANAN").

Keterangan Gambar 4.18 Proses Liveness Detection

#### 4.2.7 Proses Voting

Setelah proses autentikasi wajah dan *liveness detection* berhasil, pemilih diarahkan ke halaman *booth* voting. Pada halaman ini, pengguna dapat melihat daftar kandidat sesuai jabatan yang dibuka dalam sesi pemilihan aktif. Setelah memilih kandidat, suara dikirim ke backend dan disimpan pada tabel `votes`.

Sistem juga memperbarui status pemilih pada tabel `voter_statuses` dan atribut `has_voted` pada tabel pengguna agar pemilih tidak dapat memberikan suara lebih dari satu kali. Mekanisme ini penting untuk menjaga integritas hasil pemilihan.

```mermaid
flowchart TD
    A["Pemilih lolos verifikasi"] --> B["Masuk halaman booth"]
    B --> C["Pilih kandidat"]
    C --> D["Kirim suara ke backend"]
    D --> E["Simpan ke tabel votes"]
    E --> F["Update status sudah memilih"]
    F --> G["Tampilkan pesan berhasil"]
```

Keterangan Gambar 4.4 Alur Proses Voting

> 📸 **[SS-15]** Halaman booth voting — tangkap daftar kandidat per jabatan beserta tombol pilih (`/booth`).

Keterangan Gambar 4.19 Proses Pemungutan Suara (Voting)

#### 4.2.8 Dashboard Panitia

Dashboard panitia digunakan untuk mengelola data yang terkait dengan pemilihan. Fitur yang tersedia meliputi pengelolaan data mahasiswa, pengelolaan kandidat, pengelolaan sesi pemilihan, pemantauan suara yang masuk, dan rekapitulasi hasil voting.

Pada halaman pengelolaan mahasiswa, panitia dapat melihat daftar pemilih, status registrasi wajah, status memilih, serta kondisi akun yang terkunci. Pada halaman pengelolaan kandidat, panitia dapat menambah, mengubah, dan menghapus data kandidat sesuai jabatan. Sementara itu, pada halaman rekapitulasi, panitia dapat melihat total suara per kandidat dan hasil akhir pemilihan.

> 📸 Tangkapan layar untuk bagian ini memakai SS-05 (dashboard panitia), SS-06 (pengelolaan kandidat), SS-07 (pengelolaan mahasiswa), dan SS-08 (rekapitulasi hasil).

### 4.3 Hasil Pengujian Sistem

#### 4.3.1 Validasi Implementasi

Sebelum pengujian fungsional dilakukan, implementasi diverifikasi terlebih dahulu melalui kompilasi kode, *build* frontend, dan validasi langsung terhadap *pipeline* biometrik menggunakan model InsightFace *buffalo_l*. Hasil verifikasi menunjukkan bahwa:

1. Backend berhasil melalui pengecekan sintaks menggunakan `py_compile`.
2. Frontend berhasil dibangun menggunakan `vite build`.
3. *Pipeline* biometrik berjalan sesuai rancangan, yaitu wajah berhasil dideteksi, kelima pose registrasi diterima, pencocokan wajah yang sama menghasilkan nilai kemiripan mendekati sempurna, dan tantangan *liveness* menolak wajah netral yang tidak melakukan gerakan.

| No | Pengujian | Hasil |
|---|---|---|
| 1 | Kompilasi backend (`py_compile`) | Berhasil |
| 2 | *Build* frontend (`vite build`) | Berhasil |
| 3 | Deteksi wajah & ekstraksi embedding | Berhasil (1 wajah terdeteksi, embedding terbentuk) |
| 4 | Registrasi lima pose | Berhasil (5 dari 5 pose diterima) |
| 5 | Pencocokan wajah yang sama | Nilai kemiripan 1,00 (di atas ambang 0,35) |
| 6 | Tantangan *liveness* pada wajah netral | Sesuai (tidak lolos tanpa gerakan aktif) |

Keterangan Tabel 4.2 Hasil Validasi Implementasi

**Tangkapan layar hasil validasi yang perlu disertakan:**

- 📸 **[SS-16]** Hasil `pytest -v` — seluruh 40 test PASSED (jalankan `pytest -v` pada folder `backend`) — *Gambar 4.20 Hasil Pengujian Otomatis Seluruh Modul*.
- 📸 **[SS-17]** Hasil `vite build` berhasil (jalankan `npm run build` pada folder `mockup`) — *Gambar 4.21 Hasil Build Frontend*.
- 📸 **[SS-18]** Hasil validasi model InsightFace — nilai kemiripan 1,00 dan 5 dari 5 pose diterima — *Gambar 4.22 Hasil Validasi Model InsightFace*.

#### 4.3.2 Pengujian Fungsional

Pengujian fungsional dilakukan untuk mengetahui apakah setiap fitur sistem berjalan sesuai kebutuhan. Pengujian dilakukan berdasarkan input dan output yang dihasilkan oleh sistem.

| No | Skenario Pengujian | Input | Output yang Diharapkan | Hasil |
|---|---|---|---|---|
| 1 | Registrasi akun mahasiswa | NIM, nama, email, password | Akun mahasiswa tersimpan dan dapat login | Sesuai |
| 2 | Login mahasiswa valid | NIM dan password benar | Pengguna masuk ke dashboard mahasiswa | Sesuai |
| 3 | Login mahasiswa tidak valid | NIM atau password salah | Sistem menolak login | Sesuai |
| 4 | Registrasi wajah | Citra wajah dari kamera | *Face embedding* tersimpan pada profil wajah | Sesuai |
| 5 | Verifikasi wajah realtime | Beberapa *frame* webcam | Wajah dicocokkan dengan profil pengguna | Sesuai |
| 6 | *Liveness* acak | Gerakan wajah sesuai instruksi | Sistem memberikan status valid | Sesuai |
| 7 | Verifikasi gagal | Wajah tidak cocok atau tidak terdeteksi | Sistem menolak akses ke voting | Sesuai |
| 8 | Voting setelah verifikasi berhasil | Pemilihan kandidat | Suara tersimpan dan status berubah menjadi sudah memilih | Sesuai |
| 9 | Voting ulang oleh pemilih yang sama | Akses ulang ke booth | Sistem menolak pemungutan suara ganda | Sesuai |
| 10 | Pengelolaan kandidat oleh panitia | Tambah/ubah/hapus kandidat | Data kandidat diperbarui | Sesuai |
| 11 | Rekapitulasi hasil | Akses halaman rekapitulasi | Total suara tampil sesuai data tersimpan | Sesuai |

Keterangan Tabel 4.3 Hasil Pengujian Fungsional Sistem

Setiap baris pengujian pada tabel di atas dibuktikan dengan *unit* dan *integration test* otomatis (pytest). Tangkapan layar hasil pengujian per modul yang perlu disertakan (jalankan tiap perintah pada folder `backend`, lalu tangkap keluarannya):

- 📸 **[SS-19]** Modul Autentikasi — `pytest tests/test_modul_autentikasi.py -v` — *Gambar 4.23 Hasil Pengujian Modul Autentikasi*.
- 📸 **[SS-20]** Modul Registrasi Wajah — `pytest tests/test_modul_registrasi_wajah.py -v` — *Gambar 4.24 Hasil Pengujian Modul Registrasi Wajah*.
- 📸 **[SS-21]** Modul Verifikasi & Liveness — `pytest tests/test_modul_verifikasi_liveness.py -v` — *Gambar 4.25 Hasil Pengujian Modul Verifikasi & Liveness*.
- 📸 **[SS-22]** Modul Pemungutan Suara — `pytest tests/test_modul_voting.py -v` — *Gambar 4.26 Hasil Pengujian Modul Pemungutan Suara*.
- 📸 **[SS-23]** Modul Panitia/Admin — `pytest tests/test_modul_admin.py -v` — *Gambar 4.27 Hasil Pengujian Modul Panitia/Admin*.
- 📸 **[SS-24]** Modul Keamanan — `pytest tests/test_modul_keamanan.py -v` — *Gambar 4.28 Hasil Pengujian Modul Keamanan*.
- 📸 **[SS-25]** Modul Face Service (unit algoritma) — `pytest tests/test_face_service.py -v` — *Gambar 4.29 Hasil Pengujian Modul Face Service*.

#### 4.3.3 Pengujian Alur Realtime

Pengujian alur realtime dilakukan untuk memastikan bahwa sistem mampu menjalankan proses identifikasi wajah secara bertahap, yaitu verifikasi wajah terlebih dahulu lalu *liveness detection* satu kali secara otomatis. Hasil pengujian menunjukkan bahwa:

1. Kamera dapat aktif dan menampilkan pratinjau kepada pengguna.
2. Sistem mampu mengambil beberapa *frame* wajah secara berurutan.
3. Sistem dapat mengirim *frame* tersebut ke backend untuk dianalisis.
4. Setelah wajah cocok, sistem langsung memunculkan tantangan *liveness* acak.
5. Jika tantangan berhasil dijalankan, sistem memberikan akses ke halaman voting.

| No | Tahap Pengujian | Kondisi | Hasil |
|---|---|---|---|
| 1 | Pengambilan *frame* realtime | Kamera aktif | Berhasil |
| 2 | Pencocokan wajah | Wajah terdaftar dan jelas | Berhasil |
| 3 | Tantangan *liveness* acak | Challenge muncul otomatis | Berhasil |
| 4 | Validasi *liveness* | Pengguna mengikuti instruksi | Berhasil |
| 5 | Akses ke halaman voting | Semua validasi lolos | Berhasil |

Keterangan Tabel 4.4 Hasil Pengujian Alur Realtime

> 📸 **[SS-26]** Alur realtime di browser — tangkap urutan singkat: pemindaian wajah → wajah cocok → tantangan liveness muncul → akses voting diberikan (dapat berupa 2–3 tangkapan berurutan).

Keterangan Gambar 4.30 Alur Verifikasi Realtime pada Peramban

#### 4.3.4 Pembatasan Satu Pemilih Satu Suara

Pengujian ini dilakukan untuk memastikan bahwa sistem tidak mengizinkan seorang pemilih memberikan suara lebih dari satu kali. Setelah suara berhasil disimpan, status pemilih diperbarui sehingga akses ulang ke halaman voting akan ditolak. Hasil pengujian menunjukkan bahwa mekanisme pembatasan suara bekerja sesuai rancangan.

### 4.4 Pembahasan

Berdasarkan hasil implementasi dan pengujian, sistem *e-voting* yang dibangun telah memenuhi tujuan penelitian, yaitu menyediakan mekanisme pemilihan yang lebih aman, efisien, dan terstruktur. Integrasi antara pengenalan wajah berbasis InsightFace dan *liveness detection* membantu meningkatkan keamanan autentikasi pemilih karena sistem tidak hanya mengenali identitas, tetapi juga memeriksa keaslian wajah yang digunakan.

Penggunaan verifikasi wajah secara *realtime* memberikan beberapa keuntungan. Pertama, proses verifikasi menjadi lebih natural karena sistem menangkap aliran *frame* kamera, bukan hanya satu gambar statis. Kedua, karena data wajah pada tahap registrasi disimpan dari lima sudut (tengah, atas, bawah, kiri, dan kanan) dan pencocokan mengambil kemiripan tertinggi di antara sudut-sudut tersebut, proses menjadi lebih toleran terhadap perubahan pencahayaan maupun posisi kepala di antara *frame*. Ketiga, proses ini mendukung pengalaman pengguna yang lebih baik karena verifikasi dilakukan langsung melalui kamera tanpa langkah manual yang berlebihan.

Selain itu, penerapan tantangan *liveness* acak satu kali membuat sistem lebih tahan terhadap serangan *spoofing*. Tantangan acak seperti kedip, senyum, atau menghadap ke arah tertentu membuat proses pemalsuan menjadi lebih sulit dilakukan. Hal ini relevan dengan tujuan penelitian yang menekankan pentingnya keamanan autentikasi pada sistem pemungutan suara digital.

Jika dilihat dari sisi pengelolaan data, sistem juga mampu memisahkan data identitas pemilih, data wajah, data kandidat, dan data suara. Pemisahan ini penting agar sistem tetap terstruktur dan mudah dipelihara. Data suara tersimpan terpisah dari data wajah sehingga proses voting tetap dapat diaudit tanpa mengganggu kerahasiaan pilihan pemilih.

### 4.5 Keterbatasan Implementasi

Walaupun sistem telah berhasil diimplementasikan, terdapat beberapa keterbatasan yang perlu diperhatikan, yaitu:

1. Kualitas hasil verifikasi masih bergantung pada kondisi kamera, pencahayaan, dan kestabilan posisi wajah.
2. Proses *realtime* membutuhkan perangkat kamera yang memadai agar hasil tangkapan *frame* konsisten.
3. Sistem masih difokuskan pada skala organisasi kampus dan belum dirancang untuk beban pemilih yang sangat besar.
4. Tantangan *liveness* bersifat *challenge-response* sederhana sehingga masih dapat dikembangkan lagi dengan model *anti-spoofing* yang lebih canggih.
5. Penilaian tantangan *liveness* mengandalkan ambang batas pada sudut kepala dan rasio *landmark* wajah, sehingga tantangan berbasis arah kepala cenderung paling andal, sementara deteksi senyum dan kedip masih memerlukan kalibrasi ambang batas sesuai karakteristik kamera yang digunakan.

### 4.6 Ringkasan Hasil

Hasil implementasi menunjukkan bahwa sistem *e-voting* berbasis pengenalan wajah menggunakan InsightFace dan *liveness detection* berhasil dibangun dan dijalankan sesuai kebutuhan penelitian. Sistem menyediakan registrasi wajah, verifikasi wajah *realtime*, tantangan *liveness* acak, proses voting, serta rekapitulasi hasil pada sisi panitia. Dengan demikian, sistem ini dapat menjadi solusi yang lebih aman dan efisien untuk pelaksanaan pemilihan Ketua Himpunan Mahasiswa Teknik Informatika.
