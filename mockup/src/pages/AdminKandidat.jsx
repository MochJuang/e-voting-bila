import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMockState } from '../context/MockStateContext'
import Modal from '../components/Modal'

const WARNA_OPTIONS = ['#2563eb', '#9333ea', '#ea580c', '#0d9488', '#dc2626', '#7c3aed', '#059669', '#f59e0b']

const emptyKandidat = { nama: '', nomor: 1, warna: WARNA_OPTIONS[0], visi: '' }

export default function AdminKandidat() {
  const { jabatan, addJabatan, updateJabatan, deleteJabatan, addKandidat, updateKandidat, deleteKandidat } = useMockState()

  const [jabatanModal, setJabatanModal] = useState(null) // { id?, nama }
  const [kandidatModal, setKandidatModal] = useState(null) // { jabatanId, id?, ...form }
  const [confirmDelete, setConfirmDelete] = useState(null) // { type, jabatanId, id, label }
  const [formError, setFormError] = useState('')

  const saveJabatan = async (e) => {
    e.preventDefault()
    setFormError('')
    try {
      if (jabatanModal.id) await updateJabatan(jabatanModal.id, { nama: jabatanModal.nama })
      else await addJabatan(jabatanModal.nama)
      setJabatanModal(null)
    } catch (err) {
      setFormError(err.message || 'Gagal menyimpan jabatan')
      console.error(err)
    }
  }

  const saveKandidat = async (e) => {
    e.preventDefault()
    setFormError('')
    const { jabatanId, id, ...form } = kandidatModal
    const patch = { ...form, nomor: Number(form.nomor) }
    try {
      if (id) await updateKandidat(jabatanId, id, patch)
      else await addKandidat(jabatanId, patch)
      setKandidatModal(null)
    } catch (err) {
      setFormError(err.message || 'Gagal menyimpan kandidat')
      console.error(err)
    }
  }

  const runDelete = async () => {
    if (confirmDelete.type === 'jabatan') await deleteJabatan(confirmDelete.jabatanId)
    else await deleteKandidat(confirmDelete.jabatanId, confirmDelete.id)
    setConfirmDelete(null)
  }

  return (
    <div className="min-h-svh p-4 sm:p-8 max-w-3xl mx-auto">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Kelola Kandidat</h1>
          <p className="text-sm text-slate-500">Atur jabatan dan kandidat untuk sesi pemilihan aktif.</p>
        </div>
        <div className="flex gap-2">
          <Link to="/admin/dashboard" className="rounded-lg border border-slate-300 text-slate-700 text-sm font-semibold px-4 py-2">
            Kembali
          </Link>
          <button
            onClick={() => setJabatanModal({ nama: '' })}
            className="rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold px-4 py-2"
          >
            + Tambah Jabatan
          </button>
        </div>
      </header>

      <div className="flex flex-col gap-5">
        {jabatan.map((j) => (
          <div key={j.id} className="rounded-xl border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between mb-3">
              <p className="font-semibold text-slate-900 text-sm">{j.nama}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => setJabatanModal({ id: j.id, nama: j.nama })}
                  className="text-xs font-medium text-slate-500 hover:text-slate-800"
                >
                  Ubah Nama
                </button>
                <button
                  onClick={() => setConfirmDelete({ type: 'jabatan', jabatanId: j.id, label: j.nama })}
                  className="text-xs font-medium text-red-500 hover:text-red-700"
                >
                  Hapus Jabatan
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              {j.kandidat.length === 0 && <p className="text-xs text-slate-400">Belum ada kandidat untuk jabatan ini.</p>}
              {j.kandidat.map((k) => (
                <div key={k.id} className="flex items-center gap-3 rounded-lg border border-slate-100 p-2.5">
                  <div className="w-9 h-9 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0" style={{ background: k.warna }}>
                    {k.nomor}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-slate-900 text-sm truncate">{k.nama}</p>
                    <p className="text-xs text-slate-500 truncate">{k.visi}</p>
                  </div>
                  <button
                    onClick={() => setKandidatModal({ jabatanId: j.id, id: k.id, nama: k.nama, nomor: k.nomor, warna: k.warna, visi: k.visi })}
                    className="text-xs font-medium text-slate-500 hover:text-slate-800 shrink-0"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => setConfirmDelete({ type: 'kandidat', jabatanId: j.id, id: k.id, label: k.nama })}
                    className="text-xs font-medium text-red-500 hover:text-red-700 shrink-0"
                  >
                    Hapus
                  </button>
                </div>
              ))}
            </div>

              <button
              onClick={() => {
                const nextNomor = (j.kandidat?.reduce((max, kandidat) => Math.max(max, Number(kandidat.nomor) || 0), 0) || 0) + 1
                setFormError('')
                setKandidatModal({ jabatanId: j.id, ...emptyKandidat, nomor: nextNomor })
              }}
              className="mt-3 w-full rounded-lg border border-dashed border-slate-300 text-slate-500 hover:border-purple-400 hover:text-purple-600 text-sm py-2"
            >
              + Tambah Kandidat
            </button>
          </div>
        ))}

        {jabatan.length === 0 && (
          <p className="text-sm text-slate-400 text-center py-8">Belum ada jabatan. Tambahkan jabatan untuk mulai mengatur kandidat.</p>
        )}
      </div>

      {jabatanModal && (
        <Modal title={jabatanModal.id ? 'Ubah Nama Jabatan' : 'Tambah Jabatan'} onClose={() => setJabatanModal(null)}>
          <form onSubmit={saveJabatan} className="flex flex-col gap-3">
            {formError && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{formError}</p>}
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Nama Jabatan</span>
              <input
                required
                autoFocus
                value={jabatanModal.nama}
                onChange={(e) => setJabatanModal({ ...jabatanModal, nama: e.target.value })}
                placeholder="Mis. Ketua BEM"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </label>
            <button type="submit" className="mt-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 text-sm">
              Simpan
            </button>
          </form>
        </Modal>
      )}

      {kandidatModal && (
        <Modal title={kandidatModal.id ? 'Edit Kandidat' : 'Tambah Kandidat'} onClose={() => setKandidatModal(null)}>
          <form onSubmit={saveKandidat} className="flex flex-col gap-3">
            {formError && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{formError}</p>}
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Nama Kandidat</span>
              <input
                required
                autoFocus
                value={kandidatModal.nama}
                onChange={(e) => setKandidatModal({ ...kandidatModal, nama: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Nomor Urut</span>
              <input
                required
                type="number"
                min="1"
                value={kandidatModal.nomor}
                onChange={(e) => setKandidatModal({ ...kandidatModal, nomor: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </label>
            <div className="text-left">
              <span className="text-xs font-medium text-slate-600">Warna</span>
              <div className="mt-1 flex flex-wrap gap-2">
                {WARNA_OPTIONS.map((c) => (
                  <button
                    type="button"
                    key={c}
                    onClick={() => setKandidatModal({ ...kandidatModal, warna: c })}
                    className={`w-7 h-7 rounded-full ${kandidatModal.warna === c ? 'ring-2 ring-offset-2 ring-slate-800' : ''}`}
                    style={{ background: c }}
                  />
                ))}
              </div>
            </div>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Visi Singkat</span>
              <textarea
                value={kandidatModal.visi}
                onChange={(e) => setKandidatModal({ ...kandidatModal, visi: e.target.value })}
                rows={2}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </label>
            <button type="submit" className="mt-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2.5 text-sm">
              Simpan
            </button>
          </form>
        </Modal>
      )}

      {confirmDelete && (
        <Modal title="Konfirmasi Hapus" onClose={() => setConfirmDelete(null)}>
          <p className="text-sm text-slate-500 mb-4">
            Yakin ingin menghapus <b>{confirmDelete.label}</b>? Tindakan ini tidak dapat dibatalkan.
          </p>
          <div className="flex gap-2">
            <button onClick={() => setConfirmDelete(null)} className="flex-1 rounded-lg border border-slate-300 py-2 text-sm font-medium">
              Batal
            </button>
            <button onClick={runDelete} className="flex-1 rounded-lg bg-red-600 hover:bg-red-700 text-white py-2 text-sm font-semibold">
              Hapus
            </button>
          </div>
        </Modal>
      )}
    </div>
  )
}
