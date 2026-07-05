import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

export default function Login() {
  const navigate = useNavigate()
  const { findVoter, setCurrentNim } = useMockState()
  const [nim, setNim] = useState('2141720001')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const voter = findVoter(nim)
    if (!voter) {
      setError('NIM tidak ditemukan di Daftar Pemilih Tetap.')
      return
    }
    setCurrentNim(nim)
    navigate('/dashboard')
  }

  return (
    <Screen>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Login Mahasiswa</h2>
      <p className="text-sm text-slate-500 mb-5">Masukkan NIM & password akun Anda.</p>

      <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
        <label className="block text-left">
          <span className="text-xs font-medium text-slate-600">NIM</span>
          <input
            value={nim}
            onChange={(e) => setNim(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </label>
        <label className="block text-left">
          <span className="text-xs font-medium text-slate-600">Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="•••••••• (mockup — bebas isi)"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </label>

        {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}

        <button type="submit" className="mt-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5">
          Login
        </button>
      </form>

      <div className="mt-4 text-xs text-slate-400 bg-slate-50 border border-slate-200 rounded-lg p-2">
        Coba NIM: <b>2141720001</b> (mandiri, wajah belum enroll) · <b>2141720002</b> (mandiri, sudah memilih) ·{' '}
        <b>2141720003</b> (admin-assisted)
      </div>

      <p className="text-center text-sm text-slate-500 mt-3">
        <Link to="/reset-password" className="text-blue-600 font-medium">Lupa password?</Link>
      </p>
      <p className="text-center text-sm text-slate-500 mt-1">
        Belum punya akun? <Link to="/daftar" className="text-blue-600 font-medium">Daftar</Link>
      </p>
    </Screen>
  )
}
