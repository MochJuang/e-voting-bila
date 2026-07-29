import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const LINKS = [
  { group: 'Mahasiswa — Mandiri', items: [
    ['/', 'Home'],
    ['/login', 'B. Login'],
    ['/dashboard', 'Dashboard Mahasiswa'],
    ['/registrasi-wajah', 'D/C. Registrasi Wajah'],
    ['/verifikasi-wajah', 'F/G. Verifikasi Wajah'],
    ['/booth', 'K/L. Booth Voting'],
    ['/sudah-memilih', 'X. Sudah Memilih'],
    ['/selesai', 'M/N. Selesai'],
  ]},
  { group: 'Panitia / Admin', items: [
    ['/admin/login', 'Admin Login'],
    ['/admin/dashboard', 'Admin Dashboard'],
    ['/admin/kandidat', 'Kelola Kandidat'],
    ['/admin/mahasiswa', 'Kelola Mahasiswa'],
    ['/admin/akun', 'Kelola Akun Admin'],
    ['/admin/kiosk', 'Kiosk Admin-Assisted'],
    ['/admin/rekapitulasi', 'O. Rekapitulasi'],
  ]},
]

export default function DevNav() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()

  return (
    <div className="fixed bottom-4 right-4 z-50 font-sans">
      {open && (
        <div className="mb-2 w-72 max-h-[70svh] overflow-y-auto rounded-xl border border-slate-200 bg-white shadow-2xl p-3 text-sm">
          <p className="text-[11px] uppercase tracking-wide text-slate-400 mb-2">Mockup Navigation</p>
          {LINKS.map((g) => (
            <div key={g.group} className="mb-3">
              <p className="text-xs font-semibold text-slate-500 mb-1">{g.group}</p>
              <div className="flex flex-col gap-0.5">
                {g.items.map(([to, label]) => (
                  <Link
                    key={to}
                    to={to}
                    onClick={() => setOpen(false)}
                    className={`rounded-md px-2 py-1 text-left hover:bg-slate-100 ${pathname === to ? 'bg-slate-900 text-white hover:bg-slate-900' : 'text-slate-700'}`}
                  >
                    {label}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
      <button
        onClick={() => setOpen((o) => !o)}
        className="rounded-full bg-slate-900 text-white w-12 h-12 shadow-xl flex items-center justify-center text-lg"
        title="Navigasi mockup"
      >
        {open ? '✕' : '☰'}
      </button>
    </div>
  )
}
