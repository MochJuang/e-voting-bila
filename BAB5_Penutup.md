# BAB V

## PENUTUP

### 5.1 Kesimpulan

Berdasarkan hasil implementasi dan pengujian yang telah diuraikan pada BAB IV, penelitian mengenai implementasi sistem *e-voting* berbasis pengenalan wajah menggunakan InsightFace dan *liveness detection* pada pemilihan Ketua Himpunan Mahasiswa Teknik Informatika dapat disimpulkan sebagai berikut:

1. Sistem *e-voting* berhasil dirancang dan diimplementasikan dalam bentuk aplikasi web dengan arsitektur *client-server*, menggunakan *frontend* React JS, *backend* FastAPI, dan basis data MySQL. Sistem mencakup keseluruhan alur pemilihan, yaitu pendaftaran dan pendataan pemilih, autentikasi, pemungutan suara untuk jabatan yang dibuka, hingga rekapitulasi hasil oleh panitia. Mekanisme pembatasan satu pemilih satu suara diterapkan melalui pembaruan status pemilih sehingga akses ulang ke halaman pemungutan suara ditolak. Hal ini menjawab rumusan masalah pertama.

2. Pengenalan wajah menggunakan InsightFace (model ArcFace *buffalo_l*) berhasil diterapkan sebagai metode autentikasi pemilih melalui pendekatan *face embedding*. Registrasi wajah dilakukan dari lima sudut (tengah, atas, kanan, bawah, dan kiri) sehingga data referensi lebih representatif, sedangkan verifikasi dilakukan secara *realtime* dengan mengalirkan *frame* kamera ke *backend* dan menghitung kemiripan (*cosine similarity*) terhadap embedding tersimpan. Hasil pengujian menunjukkan pencocokan wajah yang sama menghasilkan nilai kemiripan mendekati sempurna (1,00) di atas ambang batas yang ditetapkan, sementara wajah yang berbeda ditolak. Hal ini menjawab rumusan masalah kedua.

3. *Liveness detection* berhasil diterapkan sebagai lapisan keamanan tambahan untuk mencegah autentikasi palsu. Setelah wajah cocok, sistem menampilkan satu tantangan acak berupa tersenyum, menghadap ke kiri, atau menghadap ke kanan, yang dinilai di sisi *backend* dari sudut kepala serta rasio *landmark* wajah. Dengan mewajibkan gerakan aktif yang dipilih secara acak, sistem dapat menolak media statis seperti foto atau video sehingga lebih tahan terhadap serangan *spoofing* dasar. Hal ini menjawab rumusan masalah ketiga.

4. Hasil implementasi sistem menunjukkan bahwa integrasi pengenalan wajah dan *liveness detection* mampu mendukung proses pemilihan yang lebih cepat, aman, efisien, dan terstruktur. Pengujian fungsional, pengujian alur *realtime*, serta pengujian keamanan yang dibuktikan melalui serangkaian *unit* dan *integration test* otomatis menunjukkan seluruh fitur berjalan sesuai kebutuhan. Data identitas pemilih, data wajah, data kandidat, dan data suara juga dikelola secara terpisah sehingga sistem tetap terstruktur dan dapat diaudit. Hal ini menjawab rumusan masalah keempat.

Dengan demikian, seluruh tujuan penelitian telah tercapai, dan sistem *e-voting* berbasis pengenalan wajah menggunakan InsightFace dan *liveness detection* dapat menjadi alternatif solusi pemilihan yang lebih modern, akurat, dan aman pada lingkungan himpunan mahasiswa.

### 5.2 Saran

Meskipun sistem telah berhasil diimplementasikan dan diuji, masih terdapat ruang pengembangan agar sistem menjadi lebih baik. Beberapa saran untuk penelitian selanjutnya adalah sebagai berikut:

1. Metode *liveness detection* dapat dikembangkan lebih lanjut dengan menambahkan model *anti-spoofing* pasif (misalnya *Silent-Face-Anti-Spoofing*) atau menggabungkannya dengan *active liveness* secara berlapis, agar lebih tahan terhadap serangan tingkat lanjut seperti pemutaran ulang video beresolusi tinggi.

2. Ambang batas penilaian tantangan senyum sebaiknya dikalibrasi sesuai karakteristik kamera dan kondisi pencahayaan di lokasi pemilihan, karena kualitas hasil verifikasi masih dipengaruhi oleh kondisi perangkat, pencahayaan, dan kestabilan posisi wajah.

3. Aspek keamanan data dapat ditingkatkan dengan menerapkan enkripsi data biometrik (*face embedding*) saat disimpan, serta pemisahan suara dari identitas pemilih menggunakan token pemungutan suara, guna menjaga kerahasiaan pilihan sekaligus memenuhi ketentuan perlindungan data pribadi.

4. Perlu dilakukan pengujian beban (*load testing*) pada jumlah pemilih yang lebih besar untuk memastikan kestabilan dan kecepatan sistem saat digunakan secara serentak, terutama pada saat pembukaan pemungutan suara.

5. Sistem dapat dikembangkan dengan integrasi terhadap sistem akademik kampus untuk sinkronisasi data pemilih secara otomatis, serta penyediaan aplikasi berbasis *mobile* agar lebih mudah diakses.

6. Perlu disediakan jalur verifikasi manual oleh panitia sebagai *fallback* aksesibilitas bagi pemilih yang mengalami kesulitan pada proses pemindaian wajah, sehingga tidak ada pemilih sah yang terhambat memberikan suaranya.
