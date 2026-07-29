import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMockState } from '../context/MockStateContext'
import Modal from '../components/Modal'

const emptyForm = { isNew: true, id: null, username: '', role: 'admin', password: '' }

export default function AdminAkun() {
  const { listAdminAccounts, addAdminAccount, updateAdminAccount, deleteAdminAccount } = useMockState()

  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [formModal, setFormModal] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      setAccounts(await listAdminAccounts())
    } catch (err) {
      setError(err.message || 'Gagal memuat akun admin.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const saveForm = async (e) => {
    e.preventDefault()
    setError('')
    try {
      if (formModal.isNew) {
        if (!formModal.password || formModal.password.length < 6) {
          setError('Password minimal 6 karakter.')
          return
        }
        await addAdminAccount({ username: formModal.username, password: formModal.password, role: formModal.role })
      } else {
        const patch = { username: formModal.username, role: formModal.role }
        if (formModal.password) patch.password = formModal.password
        await updateAdminAccount(formModal.id, patch)
      }
      setFormModal(null)
      await load()
    } catch (err) {
      setError(err.message || 'Gagal menyimpan akun.')
    }
  }

  return (
    <div className="min-h-svh p-4 sm:p-8 max-w-3xl mx-auto">
      <header className="flex flex-wrap items-center justify-between gap-2 mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Kelola Akun Panitia</h1>
          <p className="text-sm text-slate-500">Tambah, ubah data login, dan reset password akun admin.</p>
        </div>
        <div className="flex gap-2">
          <Link to="/admin/dashboard" className="rounded-lg border border-slate-300 text-slate-700 text-sm font-semibold px-4 py-2">
            Kembali
          </Link>
          <button
            onClick={() => { setError(''); setFormModal({ ...emptyForm }) }}
            className="rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold px-4 py-2"
          >
            + Tambah Admin
          </button>
        </div>
      </header>

      {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2 mb-4">{error}</p>}

      <div className="rounded-xl border border-slate-200 bg-white overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-slate-400 border-b border-slate-100">
              <th className="py-2.5 pl-4 pr-2">Username</th>
              <th className="py-2.5 pr-2">Role</th>
              <th className="py-2.5 pr-4 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {accounts.map((a) => (
              <tr key={a.id} className="border-b border-slate-50 last:border-0">
                <td className="py-2 pl-4 pr-2 font-medium text-slate-800">{a.username}</td>
                <td className="py-2 pr-2">
                  <span className="text-xs rounded-full px-2 py-0.5 bg-orange-50 text-orange-700">{a.role}</span>
                </td>
                <td className="py-2 pr-4 text-right whitespace-nowrap">
                  <button
                    onClick={() => { setError(''); setFormModal({ isNew: false, id: a.id, username: a.username, role: a.role, password: '' }) }}
                    className="text-xs font-medium text-slate-500 hover:text-slate-800 mr-3"
                  >
                    Edit / Reset Password
                  </button>
                  <button onClick={() => setConfirmDelete(a)} className="text-xs font-medium text-red-500 hover:text-red-700">
                    Hapus
                  </button>
                </td>
              </tr>
            ))}
            {!loading && accounts.length === 0 && (
              <tr>
                <td colSpan={3} className="py-6 text-center text-sm text-slate-400">Belum ada akun admin.</td>
              </tr>
            )}
            {loading && (
              <tr>
                <td colSpan={3} className="py-6 text-center text-sm text-slate-400">Memuat…</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {formModal && (
        <Modal title={formModal.isNew ? 'Tambah Akun Admin' : 'Edit Akun Admin'} onClose={() => setFormModal(null)}>
          <form onSubmit={saveForm} className="flex flex-col gap-3">
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Username</span>
              <input
                required
                autoFocus
                value={formModal.username}
                onChange={(e) => setFormModal({ ...formModal, username: e.target.value })}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Role</span>
              <input
                value={formModal.role}
                onChange={(e) => setFormModal({ ...formModal, role: e.target.value })}
                placeholder="admin"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">{formModal.isNew ? 'Password' : 'Reset Password'}</span>
              <input
                type="text"
                value={formModal.password}
                onChange={(e) => setFormModal({ ...formModal, password: e.target.value })}
                placeholder={formModal.isNew ? 'Minimal 6 karakter' : 'Kosongkan jika tidak direset'}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
              />
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
            Yakin menghapus akun admin <b>{confirmDelete.username}</b>?
          </p>
          <div className="flex gap-2">
            <button onClick={() => setConfirmDelete(null)} className="flex-1 rounded-lg border border-slate-300 py-2 text-sm font-medium">
              Batal
            </button>
            <button
              onClick={async () => {
                setError('')
                try {
                  await deleteAdminAccount(confirmDelete.id)
                  setConfirmDelete(null)
                  await load()
                } catch (err) {
                  setError(err.message || 'Gagal menghapus akun.')
                  setConfirmDelete(null)
                }
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
