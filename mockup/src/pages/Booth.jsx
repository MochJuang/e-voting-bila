import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

export default function Booth({ onSubmitted, embedded = false }) {
  const navigate = useNavigate()
  const { currentNim, submitVotes, jabatan } = useMockState()
  const [selections, setSelections] = useState({})
  const [confirming, setConfirming] = useState(false)

  const allFilled = jabatan.every((j) => selections[j.id])

  const handleSubmit = () => {
    submitVotes(currentNim ?? '2141720001', selections)
    if (onSubmitted) return onSubmitted()
    navigate('/selesai')
  }

  const body = (
    <>
      <h2 className="text-lg font-bold text-slate-900 mb-1">Surat Suara Digital</h2>
      <p className="text-sm text-slate-500 mb-5">Pilih satu kandidat untuk setiap jabatan. Semua jabatan wajib diisi.</p>

      <div className="flex flex-col gap-5">
        {jabatan.map((j) => (
          <div key={j.id}>
            <p className="text-sm font-semibold text-slate-800 mb-2">{j.nama}</p>
            <div className="grid grid-cols-1 gap-2">
              {j.kandidat.map((k) => {
                const selected = selections[j.id] === k.id
                return (
                  <button
                    key={k.id}
                    onClick={() => setSelections((s) => ({ ...s, [j.id]: k.id }))}
                    className={`flex items-center gap-3 rounded-xl border p-3 text-left transition-colors ${
                      selected ? 'border-purple-500 bg-purple-50' : 'border-slate-200 hover:border-purple-300'
                    }`}
                  >
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0"
                      style={{ background: k.warna }}
                    >
                      {k.nomor}
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-slate-900 text-sm truncate">{k.nama}</p>
                      <p className="text-xs text-slate-500 truncate">{k.visi}</p>
                    </div>
                    {selected && <span className="ml-auto text-purple-600 text-lg">✓</span>}
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      <button
        disabled={!allFilled}
        onClick={() => setConfirming(true)}
        className="mt-6 w-full rounded-lg bg-purple-600 hover:bg-purple-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold py-2.5"
      >
        {allFilled ? 'Tinjau & Kirim Suara' : `Lengkapi ${jabatan.length - Object.keys(selections).length} jabatan lagi`}
      </button>

      {confirming && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-5 max-w-sm w-full">
            <h3 className="font-bold text-slate-900 mb-2">Konfirmasi Suara</h3>
            <p className="text-sm text-slate-500 mb-4">
              Suara tidak dapat diubah setelah dikirim. Pastikan pilihan Anda sudah benar.
            </p>
            <div className="flex gap-2">
              <button onClick={() => setConfirming(false)} className="flex-1 rounded-lg border border-slate-300 py-2 text-sm font-medium">
                Kembali
              </button>
              <button onClick={handleSubmit} className="flex-1 rounded-lg bg-purple-600 hover:bg-purple-700 text-white py-2 text-sm font-semibold">
                Kirim Suara
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )

  if (embedded) return <div>{body}</div>

  return <Screen width="max-w-xl">{body}</Screen>
}
