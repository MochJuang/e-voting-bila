import { Link } from 'react-router-dom'
import Screen from '../components/Screen'

export default function Home() {
  return (
    <Screen width="max-w-lg">
      <div className="text-center mb-8">
        <div className="mx-auto mb-4 w-14 h-14 rounded-2xl bg-indigo-600 flex items-center justify-center text-white text-2xl font-bold">B</div>
        <h1 className="text-2xl font-bold text-slate-900">Pemilihan BILA</h1>
        <p className="text-slate-500 mt-1">Sistem e-voting dengan verifikasi wajah & liveness</p>
      </div>

      <div className="flex flex-col gap-3">
        <Link
          to="/login"
          className="rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50 transition-colors p-4 text-left"
        >
          <p className="font-semibold text-slate-900">Saya Mahasiswa</p>
          <p className="text-sm text-slate-500">Login & berikan suara untuk pemilihan aktif</p>
        </Link>
        <Link
          to="/admin/login"
          className="rounded-xl border border-slate-200 hover:border-orange-400 hover:bg-orange-50 transition-colors p-4 text-left"
        >
          <p className="font-semibold text-slate-900">Saya Panitia / Admin</p>
          <p className="text-sm text-slate-500">Kelola sesi, kandidat, kiosk, dan rekapitulasi hasil</p>
        </Link>
      </div>

      <p className="text-center text-xs text-slate-400 mt-6">Mockup UI — data & alur bersifat simulasi</p>
    </Screen>
  )
}
