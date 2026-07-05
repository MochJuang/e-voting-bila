import { Link } from 'react-router-dom'
import Screen from '../components/Screen'

export default function SudahMemilih({ embedded = false }) {
  const body = (
    <div className="text-center py-4">
      <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-red-100 flex items-center justify-center text-3xl">🚫</div>
      <h2 className="text-lg font-bold text-slate-900 mb-1">Anda Sudah Memilih</h2>
      <p className="text-sm text-slate-500 mb-6">
        Sistem mencatat NIM ini sudah menyelesaikan pemungutan suara pada sesi ini. Setiap mahasiswa hanya dapat memilih satu kali.
      </p>
      {!embedded && (
        <Link to="/dashboard" className="inline-block rounded-lg bg-slate-900 text-white font-semibold px-5 py-2.5 text-sm">
          Kembali ke Dashboard
        </Link>
      )}
    </div>
  )

  if (embedded) return body

  return <Screen>{body}</Screen>
}
