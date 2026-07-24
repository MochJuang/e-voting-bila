import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMockState } from '../context/MockStateContext'
import Modal from '../components/Modal'

const emptyForm = { nim: '', nama: '', kelas: '', modeAkses: 'mandiri' }

export default function AdminMahasiswa() {
  const { dpt, addVoter, updateVoter, deleteVoter } = useMockState()

  const [formModal, setFormModal] = useState(null) // { isNew, nim, nama, kelas, modeAkses }
  const [detailModal, setDetailModal] = useState(null) // voter object
  const [confirmDelete, setConfirmDelete] = useState(null) // { nim, nama }
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')

  const filtered = dpt.filter(
    (v) => v.nim.includes(query) || v.nama.toLowerCase().includes(query.toLowerCase()) || (v.kelas ?? '').toLowerCase().includes(query.toLowerCase()),
  )

  const openAdd = () => {
    setError('')
    setFormModal({ isNew: true, ...emptyForm })
  }

  const openEdit = (v) => {
    setError('')
    setFormModal({ isNew: false, nim: v.nim, nama: v.nama, kelas: v.kelas ?? '', modeAkses: v.modeAkses })
  }

  const saveForm = async (e) => {
    e.preventDefault()
    try {
      if (formModal.isNew) {
        if (dpt.some((v) => v.nim === formModal.nim)) {
          setError('NIM sudah terdaftar di DPT.')
          return
        }
        await addVoter({
          nim: formModal.nim,
          nama: formModal.nama,
          kelas: formModal.kelas,
          modeAkses: formModal.modeAkses,
          email: `${formModal.nim}@kampus.ac.id`,
        })
      } else {
        await updateVoter(formModal.nim, {
          nama: formModal.nama,
          kelas: formModal.kelas,
          modeAkses: formModal.modeAkses,
          email: `${formModal.nim}@kampus.ac.id`,
        })
      }
      setFormModal(null)
    } catch (err) {
      setError(err.message || 'Gagal menyimpan data mahasiswa.')
    }
  }

  const mockImport = async () => {
    const n = Math.floor(Math.random() * 900 + 100)
    await addVoter({ nim: `21417200${n}`, nama: `Mahasiswa Impor ${n}`, kelas: '-', modeAkses: 'mandiri', email: `21417200${n}@kampus.ac.id` })
  }

  return (
    <div className="min-h-svh p-4 sm:p-8 max-w-4xl mx-auto">
      <header className="flex flex-wrap items-center justify-between gap-2 mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Kelola Mahasiswa</h1>
          <p className="text-sm text-slate-500">Daftar Pemilih Tetap (DPT) &amp; mode akses per mahasiswa.</p>
        </div>
        <div className="flex gap-2">
          <Link to="/admin/dashboard" className="rounded-lg border border-slate-300 text-slate-700 text-sm font-semibold px-4 py-2">
            Kembali
          </Link>
          <button onClick={mockImport} className="rounded-lg border border-slate-300 text-slate-700 text-sm font-semibold px-4 py-2">
            Impor CSV (demo)
          </button>
          <button onClick={openAdd} className="rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold px-4 py-2">
            + Tambah Mahasiswa
          </button>
        </div>
      </header>

      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Cari NIM, nama, atau kelas…"
        className="mb-4 w-full max-w-sm rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
      />

      <div className="rounded-xl border border-slate-200 bg-white overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-slate-400 border-b border-slate-100">
              <th className="py-2.5 pl-4 pr-2">NIM</th>
              <th className="py-2.5 pr-2">Nama</th>
              <th className="py-2.5 pr-2">Kelas</th>
              <th className="py-2.5 pr-2">Mode Akses</th>
              <th className="py-2.5 pr-2">Wajah</th>
              <th className="py-2.5 pr-2">Status</th>
              <th className="py-2.5 pr-4 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((v) => (
              <tr key={v.nim} className="border-b border-slate-50 last:border-0">
                <td className="py-2 pl-4 pr-2 font-mono text-xs">{v.nim}</td>
                <td className="py-2 pr-2">{v.nama}</td>
                <td className="py-2 pr-2 text-slate-600">{v.kelas || '-'}</td>
                <td className="py-2 pr-2">
                  <span
                    className={`text-xs rounded-full px-2 py-0.5 ${
                      v.modeAkses === 'admin_assisted' ? 'bg-purple-50 text-purple-700' : 'bg-blue-50 text-blue-700'
                    }`}
                  >
                    {v.modeAkses}
                  </span>
                </td>
                <td className="py-2 pr-2">{v.faceEnrolled ? '✓' : '—'}</td>
                <td className="py-2 pr-2">
                  <span className={`text-xs rounded-full px-2 py-0.5 ${v.hasVoted ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                    {v.hasVoted ? 'Sudah Memilih' : 'Belum'}
                  </span>
                </td>
                <td className="py-2 pr-4 text-right whitespace-nowrap">
                  <button onClick={() => setDetailModal(v)} className="text-xs font-medium text-blue-600 hover:text-blue-800 mr-3">
                    Detail
                  </button>
                  <button onClick={() => openEdit(v)} className="text-xs font-medium text-slate-500 hover:text-slate-800 mr-3">
                    Edit
                  </button>
                  <button onClick={() => setConfirmDelete({ nim: v.nim, nama: v.nama })} className="text-xs font-medium text-red-500 hover:text-red-700">
                    Hapus
                  </button>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="py-6 text-center text-sm text-slate-400">
                  Tidak ada mahasiswa yang cocok.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {detailModal && (
        <Modal title="Detail Mahasiswa" onClose={() => setDetailModal(null)}>
          <div className="flex flex-col items-center mb-4">
            <div className="w-28 h-28 rounded-xl overflow-hidden bg-slate-100 border border-slate-200 flex items-center justify-center mb-2">
              {detailModal.fotoWajah ? (
                <img src={detailModal.fotoWajah} alt={`Foto registrasi ${detailModal.nama}`} className="w-full h-full object-cover" />
              ) : (
                <span className="text-xs text-slate-400 text-center px-2">Belum ada foto registrasi</span>
              )}
            </div>
            <span
              className={`text-xs rounded-full px-2 py-0.5 ${
                detailModal.faceEnrolled ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'
              }`}
            >
              {detailModal.faceEnrolled ? '✓ Wajah terdaftar' : 'Wajah belum terdaftar'}
            </span>
          </div>

          <dl className="flex flex-col gap-2 text-sm mb-5">
            <Row label="NIM" value={detailModal.nim} mono />
            <Row label="Nama Lengkap" value={detailModal.nama} />
            <Row label="Kelas" value={detailModal.kelas || '-'} />
            <Row
              label="Mode Akses"
              value={detailModal.modeAkses === 'admin_assisted' ? 'Admin-Assisted' : 'Mandiri'}
            />
            <Row label="Status Suara" value={detailModal.hasVoted ? 'Sudah Memilih' : 'Belum Memilih'} />
          </dl>

          <button
            onClick={() => {
              setDetailModal(null)
              openEdit(detailModal)
            }}
            className="w-full rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-semibold py-2"
          >
            Edit Data Ini
          </button>
        </Modal>
      )}

      {formModal && (
        <Modal title={formModal.isNew ? 'Tambah Mahasiswa' : 'Edit Mahasiswa'} onClose={() => setFormModal(null)}>
          <form onSubmit={saveForm} className="flex flex-col gap-3">
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">NIM</span>
              <input
                required
                disabled={!formModal.isNew}
                autoFocus={formModal.isNew}
                value={formModal.nim}
                onChange={(e) => setFormModal({ ...formModal, nim: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 disabled:bg-slate-50 disabled:text-slate-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Nama Lengkap</span>
              <input
                required
                autoFocus={!formModal.isNew}
                value={formModal.nama}
                onChange={(e) => setFormModal({ ...formModal, nama: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Kelas</span>
              <input
                required
                value={formModal.kelas}
                onChange={(e) => setFormModal({ ...formModal, kelas: e.target.value })}
                placeholder="Mis. TI-3A"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Mode Akses</span>
              <select
                value={formModal.modeAkses}
                onChange={(e) => setFormModal({ ...formModal, modeAkses: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              >
                <option value="mandiri">Mandiri (login sendiri, NIM &amp; password)</option>
                <option value="admin_assisted">Admin-Assisted (wajib lewat kiosk panitia)</option>
              </select>
            </label>
            {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
            <button type="submit" className="mt-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 text-sm">
              Simpan
            </button>
          </form>
        </Modal>
      )}

      {confirmDelete && (
        <Modal title="Konfirmasi Hapus" onClose={() => setConfirmDelete(null)}>
          <p className="text-sm text-slate-500 mb-4">
            Yakin ingin menghapus <b>{confirmDelete.nama}</b> ({confirmDelete.nim}) dari DPT? Tindakan ini tidak dapat dibatalkan.
          </p>
          <div className="flex gap-2">
            <button onClick={() => setConfirmDelete(null)} className="flex-1 rounded-lg border border-slate-300 py-2 text-sm font-medium">
              Batal
            </button>
              <button
                onClick={async () => {
                  await deleteVoter(confirmDelete.nim)
                  setConfirmDelete(null)
                }}
                className="flex-1 rounded-lg bg-red-600 hover:bg-red-700 text-white py-2 text-sm font-semibold"
              >
                Hapus
              </button>
          </div>
        </Modal>
      )}
    </div>
  )
}

function Row({ label, value, mono }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 pb-2">
      <dt className="text-slate-400">{label}</dt>
      <dd className={`font-medium text-slate-800 ${mono ? 'font-mono text-xs' : ''}`}>{value}</dd>
    </div>
  )
}
