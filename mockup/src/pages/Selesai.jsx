import { Link } from 'react-router-dom'
import Screen from '../components/Screen'

export default function Selesai({ embedded = false }) {
  const token = 'VT-' + Math.random().toString(36).slice(2, 10).toUpperCase()

  const body = (
    <div className="text-center py-4">
      <div className="mx-auto mb-4 w-16 h-16 rounded-full bg-orange-100 flex items-center justify-center text-3xl">✅</div>
      <h2 className="text-lg font-bold text-slate-900 mb-1">Suara Anda Tersimpan</h2>
      <p className="text-sm text-slate-500 mb-4">
        Terima kasih telah berpartisipasi. Pilihan Anda disimpan secara anonim dan tidak dapat ditelusuri kembali ke identitas Anda.
      </p>
      <div className="rounded-lg bg-slate-50 border border-slate-200 p-3 text-xs text-slate-500 mb-6">
        Kode referensi (bukti submit, bukan bukti pilihan): <span className="font-mono font-semibold text-slate-700">{token}</span>
      </div>
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
