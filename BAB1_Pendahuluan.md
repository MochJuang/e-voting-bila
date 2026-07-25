# BAB I

## PENDAHULUAN

### 1.1 Latar Belakang

Perkembangan teknologi informasi telah mendorong perubahan yang signifikan dalam berbagai bidang, termasuk dalam pelaksanaan kegiatan organisasi dan proses pengambilan keputusan secara demokratis. Salah satu bentuk penerapan teknologi tersebut adalah penggunaan sistem *electronic voting* (*e-voting*), yaitu sistem pemungutan suara berbasis elektronik yang dirancang untuk meningkatkan efisiensi, kecepatan, dan akurasi dibandingkan dengan metode pemilihan konvensional.

Di lingkungan perguruan tinggi, pemilihan Ketua Himpunan Mahasiswa Teknik Informatika merupakan salah satu kegiatan organisasi yang penting karena berkaitan dengan proses regenerasi kepemimpinan, representasi aspirasi mahasiswa, dan keberlangsungan program kerja organisasi. Namun, dalam pelaksanaannya, proses pemilihan masih sering dilakukan secara manual, mulai dari pendataan pemilih, verifikasi identitas, proses pemungutan suara, hingga perhitungan hasil. Metode tersebut memiliki beberapa kelemahan, seperti membutuhkan waktu yang relatif lama, berpotensi menimbulkan kesalahan manusia, serta membuka peluang terjadinya penyalahgunaan hak pilih, seperti pemilih ganda atau penggunaan identitas oleh pihak yang tidak berhak.

Penerapan sistem *e-voting* menjadi salah satu solusi yang dapat digunakan untuk mengatasi permasalahan tersebut. Dengan sistem *e-voting*, proses pemilihan dapat dilakukan secara lebih cepat, praktis, dan terstruktur. Selain itu, hasil pemungutan suara juga dapat direkapitulasi secara otomatis sehingga memudahkan panitia dalam pengelolaan data dan penyampaian hasil pemilihan. Meskipun demikian, keberhasilan sistem *e-voting* tidak hanya ditentukan oleh kemudahan penggunaan, tetapi juga sangat bergantung pada aspek keamanan, khususnya dalam proses autentikasi pemilih.

Salah satu teknologi yang dapat digunakan untuk mendukung autentikasi pemilih adalah pengenalan wajah (*face recognition*). Teknologi ini termasuk ke dalam sistem biometrik yang bekerja dengan mengenali identitas seseorang berdasarkan karakteristik unik pada wajah. Dalam penelitian ini, teknologi pengenalan wajah diimplementasikan menggunakan **InsightFace** dengan pendekatan ekstraksi ciri wajah ke dalam bentuk vektor wajah (*face embedding*). Pendekatan ini dinilai relevan karena proses identifikasi dilakukan dengan membandingkan vektor wajah hasil pemindaian dengan vektor wajah yang telah tersimpan di basis data, sehingga pengelolaan data menjadi lebih sederhana dan tidak memerlukan manajemen dataset pelatihan yang rumit pada sisi implementasi sistem. Dengan demikian, InsightFace dapat mendukung proses verifikasi identitas pemilih secara otomatis, efisien, dan lebih praktis untuk diterapkan pada lingkungan pemilihan skala kampus.

Namun demikian, penggunaan pengenalan wajah saja belum sepenuhnya menjamin keamanan sistem. Sistem masih berpotensi mengalami serangan *spoofing*, yaitu upaya pemalsuan identitas menggunakan media seperti foto, video, atau tampilan wajah tiruan lainnya untuk mengelabui proses autentikasi. Kondisi ini dapat menurunkan tingkat keabsahan pemilih dan membuka peluang terjadinya kecurangan dalam proses pemungutan suara.

Untuk mengatasi kelemahan tersebut, diperlukan mekanisme tambahan berupa *liveness detection*. *Liveness detection* merupakan metode yang digunakan untuk memastikan bahwa wajah yang terdeteksi oleh sistem merupakan wajah asli dari pengguna yang hadir secara langsung, bukan representasi palsu dari media tertentu. Dengan adanya *liveness detection*, sistem tidak hanya memverifikasi kecocokan identitas wajah, tetapi juga memastikan keaslian objek yang melakukan autentikasi.

Berdasarkan uraian tersebut, penelitian ini berfokus pada implementasi sistem *e-voting* berbasis pengenalan wajah menggunakan InsightFace dan *liveness detection* pada pemilihan Ketua Himpunan Mahasiswa Teknik Informatika. Sistem yang dibangun diharapkan mampu meningkatkan efisiensi proses pemilihan, memperkuat keamanan autentikasi pemilih, meminimalkan peluang penyalahgunaan hak pilih, serta mendukung pelaksanaan pemilihan yang lebih modern, akurat, dan terpercaya.

### 1.2 Identifikasi Masalah

Berdasarkan latar belakang tersebut, identifikasi masalah dalam penelitian ini adalah sebagai berikut:

1. Proses pemilihan Ketua Himpunan Mahasiswa Teknik Informatika masih dilakukan secara manual sehingga kurang efisien dari segi waktu dan pengelolaan data.
2. Verifikasi identitas pemilih pada sistem konvensional masih berpotensi menimbulkan kesalahan dan penyalahgunaan hak pilih.
3. Sistem *e-voting* membutuhkan mekanisme autentikasi yang akurat agar hanya pemilih yang sah yang dapat memberikan suara.
4. Penerapan pengenalan wajah tanpa pengujian keaslian wajah masih rentan terhadap serangan *spoofing*.
5. Diperlukan integrasi teknologi InsightFace dan *liveness detection* agar proses autentikasi pada sistem *e-voting* menjadi lebih aman dan andal.

### 1.3 Rumusan Masalah

Rumusan masalah dalam penelitian ini adalah sebagai berikut:

1. Bagaimana mengimplementasikan sistem *e-voting* pada pemilihan Ketua Himpunan Mahasiswa Teknik Informatika?
2. Bagaimana menerapkan pengenalan wajah menggunakan InsightFace sebagai metode autentikasi pemilih pada sistem *e-voting*?
3. Bagaimana menerapkan *liveness detection* untuk mencegah autentikasi palsu pada sistem?
4. Bagaimana hasil implementasi sistem *e-voting* berbasis pengenalan wajah menggunakan InsightFace dan *liveness detection* pada studi kasus yang diteliti?

### 1.4 Batasan Masalah

Agar penelitian lebih terarah dan tidak menyimpang dari tujuan utama, maka batasan masalah dalam penelitian ini adalah sebagai berikut:

1. Penelitian difokuskan pada implementasi sistem *e-voting* untuk pemilihan Ketua Himpunan Mahasiswa Teknik Informatika.
2. Sistem yang dibangun mencakup pendataan pemilih, autentikasi pemilih, proses pemungutan suara, dan rekapitulasi hasil.
3. Autentikasi pemilih dilakukan menggunakan teknologi pengenalan wajah berbasis InsightFace.
4. Validasi keaslian wajah dilakukan menggunakan metode *liveness detection*.
5. Setiap pemilih hanya dapat memberikan suara satu kali.
6. Penelitian tidak membahas keamanan jaringan, enkripsi data tingkat lanjut, maupun integrasi dengan sistem eksternal secara mendalam.
7. Implementasi sistem difokuskan pada lingkungan terbatas sesuai kebutuhan studi kasus penelitian.

### 1.5 Tujuan Penelitian

Tujuan penelitian ini adalah sebagai berikut:

1. Merancang dan mengimplementasikan sistem *e-voting* untuk pemilihan Ketua Himpunan Mahasiswa Teknik Informatika.
2. Menerapkan teknologi pengenalan wajah menggunakan InsightFace sebagai metode autentikasi pemilih.
3. Menerapkan *liveness detection* untuk meningkatkan keamanan sistem terhadap serangan *spoofing*.
4. Menguji sistem dalam mendukung proses pemilihan yang lebih cepat, aman, efisien, dan terstruktur.

### 1.6 Manfaat Penelitian

#### 1.6.1 Manfaat Teoritis

Penelitian ini diharapkan dapat menambah referensi ilmiah dalam pengembangan sistem *e-voting* yang memanfaatkan teknologi biometrik, khususnya pengenalan wajah berbasis InsightFace dan *liveness detection*, serta menjadi bahan kajian untuk penelitian selanjutnya pada bidang sistem keamanan dan autentikasi digital.

#### 1.6.2 Manfaat Praktis

1. Bagi himpunan mahasiswa, penelitian ini dapat menjadi alternatif sistem pemilihan yang lebih modern, cepat, dan efisien.
2. Bagi panitia pemilihan, sistem ini dapat membantu proses verifikasi pemilih, pemungutan suara, dan rekapitulasi hasil secara lebih terstruktur.
3. Bagi pemilih, sistem ini memberikan kemudahan dalam proses autentikasi dan pemilihan dengan tingkat keamanan yang lebih baik.
4. Bagi peneliti selanjutnya, penelitian ini dapat menjadi dasar pengembangan sistem autentikasi biometrik pada aplikasi pemilihan atau sistem serupa.

### 1.7 Sistematika Penulisan

Sistematika penulisan skripsi ini disusun sebagai berikut:

**BAB I Pendahuluan**, berisi latar belakang, identifikasi masalah, rumusan masalah, batasan masalah, tujuan penelitian, manfaat penelitian, dan sistematika penulisan.

**BAB II Tinjauan Pustaka**, berisi penelitian terdahulu, landasan teori, dan kerangka pemikiran yang mendukung penelitian.

**BAB III Metodologi Penelitian**, berisi jenis penelitian, objek penelitian, teknik pengumpulan data, tahapan penelitian, metode pengembangan sistem, analisis kebutuhan, serta perancangan sistem.

**BAB IV Hasil dan Pembahasan**, berisi hasil implementasi sistem, hasil pengujian, serta analisis terhadap kinerja sistem *e-voting* berbasis pengenalan wajah menggunakan InsightFace dan *liveness detection*.

**BAB V Penutup**, berisi kesimpulan dari hasil penelitian dan saran untuk pengembangan penelitian selanjutnya.
