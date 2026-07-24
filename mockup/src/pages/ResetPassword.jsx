import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

export default function ResetPassword() {
  const navigate = useNavigate()
  const { requestPasswordReset, confirmPasswordReset } = useMockState()
  const [step, setStep] = useState('request') // request | kode | selesai
  const [nim, setNim] = useState('')
  const [error, setError] = useState('')
  const [kode, setKode] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)

  const requestKode = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await requestPasswordReset(nim)
      setStep('kode')
    } catch (err) {
      setError(err.message || 'Gagal meminta kode reset.')
    } finally {
      setLoading(false)
    }
  }

  const submitReset = async (e) => {
    e.preventDefault()
    if (password.length < 8) {
      setError('Password minimal 8 karakter.')
      return
    }
    if (password !== confirm) {
      setError('Konfirmasi password tidak cocok.')
      return
    }
    setLoading(true)
    setError('')
    try {
      await confirmPasswordReset({ nim, code: kode, new_password: password })
      setStep('selesai')
    } catch (err) {
      setError(err.message || 'Gagal reset password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Screen>
      <h2 className="text-lg font-bold text-slate-900 mb-1">Reset Password</h2>

      {step === 'request' && (
        <>
          <p className="text-sm text-slate-500 mb-5">Masukkan NIM Anda, kami akan mengirimkan kode verifikasi ke email kampus terdaftar.</p>
          <form onSubmit={requestKode} className="flex flex-col gap-3">
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">NIM</span>
              <input
                required
                value={nim}
                onChange={(e) => setNim(e.target.value)}
                placeholder="2141720001"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>
            {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
            <button type="submit" disabled={loading} className="mt-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-2.5">
              {loading ? 'Memproses...' : 'Kirim Kode Verifikasi'}
            </button>
          </form>
        </>
      )}

      {step === 'kode' && (
        <>
          <p className="text-sm text-slate-500 mb-5">
            Kode verifikasi (demo: <b>123456</b>) telah dikirim ke email kampus untuk NIM <b>{nim}</b>. Masukkan kode dan password baru Anda.
          </p>
          <form onSubmit={submitReset} className="flex flex-col gap-3">
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Kode Verifikasi</span>
              <input
                required
                value={kode}
                onChange={(e) => setKode(e.target.value)}
                placeholder="123456"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Password Baru</span>
              <input
                required
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimal 8 karakter"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>
            <label className="block text-left">
              <span className="text-xs font-medium text-slate-600">Konfirmasi Password Baru</span>
              <input
                required
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </label>
            {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
            <button type="submit" disabled={loading} className="mt-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-2.5">
              {loading ? 'Memproses...' : 'Simpan Password Baru'}
            </button>
          </form>
        </>
      )}

      {step === 'selesai' && (
        <div className="text-center py-4">
          <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-green-100 flex items-center justify-center text-3xl">✅</div>
          <p className="font-semibold text-slate-900 mb-1">Password Berhasil Direset</p>
          <p className="text-sm text-slate-500 mb-6">Silakan login kembali menggunakan password baru Anda.</p>
          <button
            onClick={() => navigate('/login')}
            className="inline-block rounded-lg bg-slate-900 text-white font-semibold px-5 py-2.5 text-sm"
          >
            Kembali ke Login
          </button>
        </div>
      )}

      {step !== 'selesai' && (
        <p className="text-center text-sm text-slate-500 mt-4">
          Sudah ingat password? <Link to="/login" className="text-blue-600 font-medium">Login</Link>
        </p>
      )}
    </Screen>
  )
}
