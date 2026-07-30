import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'
import Modal from '../components/Modal'
import { useMockState } from '../context/MockStateContext'

export default function MahasiswaDashboard() {
  const navigate = useNavigate()
  const { currentNim, currentUser, findVoter, logoutStudent, changePassword, getMyFacePhoto } = useMockState()
  const voter = currentUser || findVoter(currentNim) || findVoter('2141720001')

  const [facePhoto, setFacePhoto] = useState(null)

  useEffect(() => {
    if (!voter?.faceEnrolled) {
      setFacePhoto(null)
      return
    }
    let cancelled = false
    getMyFacePhoto()
      .then((data) => {
        if (!cancelled) setFacePhoto(data)
      })
      .catch(() => {
        if (!cancelled) setFacePhoto(null)
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [voter?.faceEnrolled, voter?.hasVoted])

  const [passwordModal, setPasswordModal] = useState(false)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')
  const [passwordLoading, setPasswordLoading] = useState(false)

  const closePasswordModal = () => {
    setPasswordModal(false)
    setCurrentPassword('')
    setNewPassword('')
    setConfirmPassword('')
    setPasswordError('')
    setPasswordSuccess('')
  }

  const submitChangePassword = async (e) => {
    e.preventDefault()
    setPasswordError('')
    setPasswordSuccess('')
    if (newPassword.length < 8) {
      setPasswordError('Password baru minimal 8 karakter.')
      return
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('Konfirmasi password baru tidak cocok.')
      return
    }
    setPasswordLoading(true)
    try {
      await changePassword({ currentPassword, newPassword })
      setPasswordSuccess('Password berhasil diganti.')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      setPasswordError(err.message || 'Gagal mengganti password.')
    } finally {
      setPasswordLoading(false)
    }
  }

  const isAssisted = voter?.modeAkses === 'admin_assisted'

  const logout = () => {
    logoutStudent()
    navigate('/')
  }

  return (
    <Screen width="max-w-lg">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-xs text-slate-400">Selamat datang,</p>
          <h2 className="text-lg font-bold text-slate-900">{voter?.nama}</h2>
          <p className="text-xs text-slate-500 font-mono">{voter?.nim}</p>
        </div>
        <span
          className={`text-xs rounded-full px-2.5 py-1 font-medium ${
            isAssisted ? 'bg-purple-50 text-purple-700' : 'bg-blue-50 text-blue-700'
          }`}
        >
          {isAssisted ? 'Admin-Assisted' : 'Mandiri'}
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {/* Registrasi */}
        <div className="rounded-xl border border-slate-200 p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              {voter?.faceEnrolled && (
                <div className="shrink-0 w-14 h-14 rounded-lg overflow-hidden bg-slate-100 border border-slate-200">
                  {facePhoto?.enrolled_photo ? (
                    <img src={facePhoto.enrolled_photo} alt="Foto registrasi wajah" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-300 text-xs">…</div>
                  )}
                </div>
              )}
              <div>
                <p className="font-semibold text-slate-900 text-sm">Registrasi Wajah</p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {voter?.faceEnrolled ? 'Wajah Anda sudah terdaftar di sistem.' : 'Anda belum mendaftarkan wajah. Wajib dilakukan sebelum memilih.'}
                </p>
              </div>
            </div>
            <span className={`shrink-0 text-xs rounded-full px-2 py-0.5 ${voter?.faceEnrolled ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
              {voter?.faceEnrolled ? '✓ Terdaftar' : 'Belum'}
            </span>
          </div>
          <button
            onClick={() => navigate('/registrasi-wajah')}
            className="mt-3 w-full rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold py-2"
          >
            {voter?.faceEnrolled ? 'Update Ulang Wajah' : 'Mulai Registrasi Wajah'}
          </button>
        </div>

        {/* Pemilihan */}
        <div className={`rounded-xl border p-4 ${isAssisted ? 'border-slate-200 bg-slate-50' : 'border-slate-200'}`}>
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="font-semibold text-slate-900 text-sm">Pemilihan</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {isAssisted
                  ? 'Mode akses Anda "Admin-Assisted" — pemungutan suara wajib dilakukan di kiosk panitia, tidak bisa lewat halaman ini.'
                  : voter?.hasVoted
                  ? 'Anda sudah menyelesaikan pemungutan suara pada sesi ini.'
                  : 'Berikan suara Anda untuk seluruh jabatan yang dibuka.'}
              </p>
            </div>
            <span
              className={`shrink-0 text-xs rounded-full px-2 py-0.5 ${
                voter?.hasVoted ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'
              }`}
            >
              {voter?.hasVoted ? '✓ Sudah Memilih' : 'Belum'}
            </span>
          </div>
          <button
            disabled={isAssisted || voter?.hasVoted}
            onClick={() => navigate('/verifikasi-wajah')}
            className="mt-3 w-full rounded-lg bg-purple-600 hover:bg-purple-700 disabled:bg-slate-200 disabled:text-slate-400 text-white text-sm font-semibold py-2"
          >
            {isAssisted ? 'Kunjungi Kiosk Panitia' : voter?.hasVoted ? 'Sudah Memilih' : 'Mulai Verifikasi & Pilih'}
          </button>

          {facePhoto?.last_verification_photo && (
            <div className="mt-3 flex items-center gap-3 rounded-lg bg-slate-50 border border-slate-100 p-2.5">
              <img
                src={facePhoto.last_verification_photo}
                alt="Wajah saat verifikasi terakhir"
                className="w-12 h-12 rounded-lg object-cover border border-slate-200"
              />
              <div>
                <p className="text-xs font-medium text-slate-600">Wajah saat verifikasi terakhir</p>
                <p className="text-[11px] text-slate-400">
                  {new Date(facePhoto.last_verification_at).toLocaleString('id-ID')}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Ganti Password */}
        <div className="rounded-xl border border-slate-200 p-4">
          <p className="font-semibold text-slate-900 text-sm">Keamanan Akun</p>
          <p className="text-xs text-slate-500 mt-0.5">Ganti password akun Anda secara berkala.</p>
          <button
            onClick={() => setPasswordModal(true)}
            className="mt-3 w-full rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-semibold py-2"
          >
            Ganti Password
          </button>
        </div>
      </div>

      <button onClick={logout} className="mt-5 w-full text-center text-sm text-slate-400 hover:text-slate-600">
        Keluar
      </button>

      {passwordModal && (
        <Modal title="Ganti Password" onClose={closePasswordModal}>
          <form onSubmit={submitChangePassword} className="flex flex-col gap-3">
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Password Saat Ini</span>
              <input
                type="password"
                required
                autoFocus
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Password Baru</span>
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Minimal 8 karakter"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Konfirmasi Password Baru</span>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>

            {passwordError && (
              <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">{passwordError}</p>
            )}
            {passwordSuccess && (
              <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-2">{passwordSuccess}</p>
            )}

            <button
              type="submit"
              disabled={passwordLoading}
              className="mt-1 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-2.5 text-sm"
            >
              {passwordLoading ? 'Menyimpan...' : 'Simpan Password Baru'}
            </button>
          </form>
        </Modal>
      )}
    </Screen>
  )
}
