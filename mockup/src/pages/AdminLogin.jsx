import { useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'
import { useState } from 'react'
import { useMockState } from '../context/MockStateContext'

export default function AdminLogin() {
  const navigate = useNavigate()
  const { loginAdmin } = useMockState()
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  return (
    <Screen>
      <div className="text-center mb-6">
        <div className="mx-auto mb-3 w-12 h-12 rounded-xl bg-orange-500 flex items-center justify-center text-white text-xl">🛡</div>
        <h2 className="text-lg font-bold text-slate-900">Login Panitia / Admin</h2>
        <p className="text-sm text-slate-500 mt-1">Akses ke dashboard pengelolaan pemilihan.</p>
      </div>

      <form
        className="flex flex-col gap-3"
        onSubmit={async (e) => {
          e.preventDefault()
          setLoading(true)
          setError('')
          const form = new FormData(e.currentTarget)
          const username = form.get('username') || 'panitia1'
          const password = form.get('password') || 'password'
          try {
            await loginAdmin({ username: String(username), password: String(password) })
            navigate('/admin/dashboard')
          } catch (err) {
            setError(err.message || 'Login admin gagal.')
          } finally {
            setLoading(false)
          }
        }}
      >
        <label className="block text-left">
          <span className="text-xs font-medium text-slate-600">Username</span>
          <input
            name="username"
            defaultValue="panitia1"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </label>
        <label className="block text-left">
          <span className="text-xs font-medium text-slate-600">Password</span>
          <input
            name="password"
            type="password"
            placeholder="•••••••• (mockup — bebas isi)"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </label>
        {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
        <button type="submit" disabled={loading} className="mt-2 rounded-lg bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white font-semibold py-2.5">
          {loading ? 'Memproses...' : 'Masuk Dashboard'}
        </button>
      </form>
    </Screen>
  )
}
