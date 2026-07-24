import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMockState } from '../context/MockStateContext'

export default function AdminDashboard() {
  const navigate = useNavigate()
  const { dpt, jabatan, logoutAdmin } = useMockState()
  const [sessionOpen, setSessionOpen] = useState(true)

  const logout = () => {
    logoutAdmin()
    navigate('/')
  }

  const total = dpt.length
  const sudahMemilih = dpt.filter((v) => v.hasVoted).length
  const mandiri = dpt.filter((v) => v.modeAkses === 'mandiri').length
  const assisted = dpt.filter((v) => v.modeAkses === 'admin_assisted').length

  return (
    <div className="min-h-svh p-4 sm:p-8 max-w-5xl mx-auto">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Dashboard Panitia</h1>
          <p className="text-sm text-slate-500">Pemilihan Ketua Himpunan — Sesi Aktif</p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/admin/kiosk" className="rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-sm font-semibold px-4 py-2">
            Buka Kiosk
          </Link>
          <Link to="/admin/rekapitulasi" className="rounded-lg bg-orange-500 hover:bg-orange-600 text-white text-sm font-semibold px-4 py-2">
            Rekapitulasi
          </Link>
          <button
            onClick={logout}
            className="rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-600 text-sm font-semibold px-4 py-2"
          >
            Logout
          </button>
        </div>
      </header>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <StatCard label="Total DPT" value={total} color="#334155" />
        <StatCard label="Sudah Memilih" value={`${sudahMemilih} / ${total}`} color="#16a34a" />
        <StatCard label="Mode Mandiri" value={mandiri} color="#2563eb" />
        <StatCard label="Mode Admin-Assisted" value={assisted} color="#9333ea" />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4 mb-6 flex items-center justify-between">
        <div>
          <p className="font-semibold text-slate-900 text-sm">Status Pemungutan Suara</p>
          <p className="text-xs text-slate-500">Buka/tutup akses booth untuk seluruh mahasiswa.</p>
        </div>
        <button
          onClick={() => setSessionOpen((s) => !s)}
          className={`rounded-full px-4 py-2 text-sm font-semibold text-white ${sessionOpen ? 'bg-green-600' : 'bg-slate-400'}`}
        >
          {sessionOpen ? 'Sedang Dibuka' : 'Ditutup'}
        </button>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4 mb-6">
        <div className="flex items-center justify-between mb-3">
          <p className="font-semibold text-slate-900 text-sm">Jabatan &amp; Kandidat</p>
          <Link to="/admin/kandidat" className="rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold px-3 py-1.5">
            Kelola Kandidat
          </Link>
        </div>
        <div className="flex flex-col gap-3">
          {jabatan.map((j) => (
            <div key={j.id} className="border border-slate-100 rounded-lg p-3">
              <p className="text-sm font-medium text-slate-800 mb-2">{j.nama}</p>
              <div className="flex flex-wrap gap-2">
                {j.kandidat.length === 0 && <span className="text-xs text-slate-400">Belum ada kandidat</span>}
                {j.kandidat.map((k) => (
                  <span key={k.id} className="inline-flex items-center gap-1.5 text-xs bg-slate-50 border border-slate-200 rounded-full px-2 py-1">
                    <span className="w-4 h-4 rounded-full text-white flex items-center justify-center text-[10px]" style={{ background: k.warna }}>
                      {k.nomor}
                    </span>
                    {k.nama}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex items-center justify-between mb-3">
          <p className="font-semibold text-slate-900 text-sm">Daftar Pemilih Tetap</p>
          <Link to="/admin/mahasiswa" className="rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold px-3 py-1.5">
            Kelola Mahasiswa
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-slate-400 border-b border-slate-100">
                <th className="py-1.5 pr-2">NIM</th>
                <th className="py-1.5 pr-2">Nama</th>
                <th className="py-1.5 pr-2">Mode Akses</th>
                <th className="py-1.5 pr-2">Wajah</th>
                <th className="py-1.5">Status</th>
              </tr>
            </thead>
            <tbody>
              {dpt.map((v) => (
                <tr key={v.nim} className="border-b border-slate-50 last:border-0">
                  <td className="py-1.5 pr-2 font-mono text-xs">{v.nim}</td>
                  <td className="py-1.5 pr-2">{v.nama}</td>
                  <td className="py-1.5 pr-2">
                    <span
                      className={`text-xs rounded-full px-2 py-0.5 ${
                        v.modeAkses === 'admin_assisted' ? 'bg-purple-50 text-purple-700' : 'bg-blue-50 text-blue-700'
                      }`}
                    >
                      {v.modeAkses}
                    </span>
                  </td>
                  <td className="py-1.5 pr-2">{v.faceEnrolled ? '✓' : '—'}</td>
                  <td className="py-1.5">
                    <span className={`text-xs rounded-full px-2 py-0.5 ${v.hasVoted ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                      {v.hasVoted ? 'Sudah Memilih' : 'Belum'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, color }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className="text-2xl font-bold" style={{ color }}>
        {value}
      </p>
    </div>
  )
}
