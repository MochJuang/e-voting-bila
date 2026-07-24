import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMockState } from '../context/MockStateContext'
import { api } from '../lib/api'

const DEMO_FALLBACK = {
  ketua: { k1: 142, k2: 98, k3: 61 },
  wakil: { w1: 176, w2: 125 },
  senator: { s1: 151, s2: 150 },
}

export default function AdminRekapitulasi() {
  const { votes, dpt, jabatan, adminToken } = useMockState()
  const [exporting, setExporting] = useState(null)
  const [exportError, setExportError] = useState('')

  const dataFor = (jabatanId) => {
    const real = votes[jabatanId]
    if (real && Object.keys(real).length) return real
    return DEMO_FALLBACK[jabatanId] || {}
  }

  const totalDpt = dpt.length
  const totalVoted = dpt.filter((v) => v.hasVoted).length

  const downloadBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  const runExport = async (kind) => {
    if (!adminToken) {
      setExportError('Silakan login sebagai panitia terlebih dahulu.')
      return
    }
    setExportError('')
    setExporting(kind)
    try {
      const sessionName = 'Pemilihan_Ketua_Himpunan_IT_2026'
      const blob =
        kind === 'pdf'
          ? await api.admin.exportPdf(adminToken)
          : await api.admin.exportExcel(adminToken)
      downloadBlob(blob, `${sessionName}.${kind === 'pdf' ? 'pdf' : 'xlsx'}`)
    } catch (err) {
      setExportError(err.message || 'Gagal mengekspor data')
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className="min-h-svh p-4 sm:p-8 max-w-3xl mx-auto">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Rekapitulasi Hasil</h1>
          <p className="text-sm text-slate-500">Pemilihan Ketua Himpunan 2026 — Sesi Ditutup</p>
        </div>
        <div className="flex gap-2">
          <Link to="/admin/dashboard" className="rounded-lg border border-slate-300 text-slate-700 text-sm font-semibold px-4 py-2">
            Kembali
          </Link>
          <button
            onClick={() => runExport('pdf')}
            disabled={exporting !== null}
            className="rounded-lg bg-orange-500 hover:bg-orange-600 disabled:opacity-60 text-white text-sm font-semibold px-4 py-2"
          >
            {exporting === 'pdf' ? 'Mengekspor...' : 'Ekspor PDF'}
          </button>
          <button
            onClick={() => runExport('excel')}
            disabled={exporting !== null}
            className="rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white text-sm font-semibold px-4 py-2"
          >
            {exporting === 'excel' ? 'Mengekspor...' : 'Ekspor Excel'}
          </button>
        </div>
      </header>

      {exportError && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 mb-6">
          {exportError}
        </div>
      )}

      <div className="rounded-xl border border-slate-200 bg-white p-4 mb-6 text-sm text-slate-600">
        Partisipasi: <b>{totalVoted}</b> dari <b>{totalDpt}</b> pemilih terdaftar (contoh data dummy digunakan untuk kandidat yang belum menerima suara pada mockup ini).
      </div>

      <div className="flex flex-col gap-6">
        {jabatan.map((j) => {
          const d = dataFor(j.id)
          const max = Math.max(1, ...Object.values(d))
          return (
            <div key={j.id} className="rounded-xl border border-slate-200 bg-white p-4">
              <p className="font-semibold text-slate-900 text-sm mb-3">{j.nama}</p>
              <div className="flex flex-col gap-2">
                {j.kandidat.map((k) => {
                  const count = d[k.id] || 0
                  const pct = Math.round((count / max) * 100)
                  return (
                    <div key={k.id} className="flex items-center gap-3">
                      <div
                        className="w-7 h-7 rounded-full flex items-center justify-center text-white font-bold text-xs shrink-0"
                        style={{ background: k.warna }}
                      >
                        {k.nomor}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between text-xs mb-0.5">
                          <span className="font-medium text-slate-700 truncate">{k.nama}</span>
                          <span className="text-slate-500">{count} suara</span>
                        </div>
                        <div className="h-2.5 rounded-full bg-slate-100 overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${pct}%`, background: k.warna }} />
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
