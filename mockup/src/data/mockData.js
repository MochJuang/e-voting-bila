export const JABATAN = [
  {
    id: 'ketua',
    nama: 'Ketua BEM',
    kandidat: [
      { id: 'k1', nama: 'Andika Pratama', nomor: 1, warna: '#2563eb', visi: 'Kampus yang lebih inklusif dan transparan.' },
      { id: 'k2', nama: 'Sarah Amelia', nomor: 2, warna: '#9333ea', visi: 'Fokus pada kesejahteraan mahasiswa.' },
      { id: 'k3', nama: 'Rizky Ramadhan', nomor: 3, warna: '#ea580c', visi: 'Digitalisasi layanan kemahasiswaan.' },
    ],
  },
  {
    id: 'wakil',
    nama: 'Wakil Ketua BEM',
    kandidat: [
      { id: 'w1', nama: 'Bunga Citra', nomor: 1, warna: '#0d9488', visi: 'Penguatan UKM dan organisasi mahasiswa.' },
      { id: 'w2', nama: 'Fajar Nugroho', nomor: 2, warna: '#dc2626', visi: 'Advokasi kebijakan kampus yang berpihak ke mahasiswa.' },
    ],
  },
  {
    id: 'senator',
    nama: 'Senator Mahasiswa',
    kandidat: [
      { id: 's1', nama: 'Dewi Lestari', nomor: 1, warna: '#7c3aed', visi: 'Representasi suara mahasiswa di senat.' },
      { id: 's2', nama: 'Galih Saputra', nomor: 2, warna: '#059669', visi: 'Transparansi anggaran kemahasiswaan.' },
    ],
  },
]

function avatarPlaceholder(initials, bg) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240"><rect width="240" height="240" fill="${bg}"/><text x="50%" y="53%" font-family="system-ui,sans-serif" font-size="88" font-weight="700" fill="#fff" text-anchor="middle" dominant-baseline="middle">${initials}</text></svg>`
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

export const MOCK_DPT = [
  {
    nim: '2141720001',
    nama: 'Ahmad Fauzan',
    kelas: 'TI-3A',
    modeAkses: 'mandiri',
    hasVoted: false,
    faceEnrolled: true,
    fotoWajah: avatarPlaceholder('AF', '#2563eb'),
  },
  {
    nim: '2141720002',
    nama: 'Siti Nurhaliza',
    kelas: 'SI-2B',
    modeAkses: 'mandiri',
    hasVoted: true,
    faceEnrolled: true,
    fotoWajah: avatarPlaceholder('SN', '#9333ea'),
  },
  {
    nim: '2141720003',
    nama: 'Budi Santoso',
    kelas: 'TI-3A',
    modeAkses: 'admin_assisted',
    hasVoted: false,
    faceEnrolled: true,
    fotoWajah: avatarPlaceholder('BS', '#0d9488'),
  },
  {
    nim: '2141720004',
    nama: 'Putri Wulandari',
    kelas: 'SI-1A',
    modeAkses: 'admin_assisted',
    hasVoted: false,
    faceEnrolled: false,
    fotoWajah: null,
  },
  {
    nim: '2141720005',
    nama: 'Reza Firmansyah',
    kelas: 'TI-2C',
    modeAkses: 'mandiri',
    hasVoted: false,
    faceEnrolled: false,
    fotoWajah: null,
  },
]

export const STAGES = [
  { key: 1, label: 'Pendaftaran', color: '#2563eb' },
  { key: 2, label: 'Verifikasi', color: '#16a34a' },
  { key: 3, label: 'Pemungutan Suara', color: '#9333ea' },
  { key: 4, label: 'Penutupan', color: '#ea580c' },
]
