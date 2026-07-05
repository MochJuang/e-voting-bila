import { useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'

export default function AdminLogin() {
  const navigate = useNavigate()

  return (
    <Screen>
      <div className="text-center mb-6">
        <div className="mx-auto mb-3 w-12 h-12 rounded-xl bg-orange-500 flex items-center justify-center text-white text-xl">🛡</div>
        <h2 className="text-lg font-bold text-slate-900">Login Panitia / Admin</h2>
        <p className="text-sm text-slate-500 mt-1">Akses ke dashboard pengelolaan pemilihan.</p>
      </div>

      <form
        className="flex flex-col gap-3"
        onSubmit={(e) => {
          e.preventDefault()
          navigate('/admin/dashboard')
        }}
      >
        <label className="block text-left">
          <span className="text-xs font-medium text-slate-600">Username</span>
          <input
            defaultValue="panitia1"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </label>
        <label className="block text-left">
          <span className="text-xs font-medium text-slate-600">Password</span>
          <input
            type="password"
            placeholder="•••••••• (mockup — bebas isi)"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          />
        </label>
        <button type="submit" className="mt-2 rounded-lg bg-orange-500 hover:bg-orange-600 text-white font-semibold py-2.5">
          Masuk Dashboard
        </button>
      </form>
    </Screen>
  )
}
