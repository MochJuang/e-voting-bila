import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

export default function VerifikasiWajah({ onValid, embedded = false }) {
  const navigate = useNavigate()
  const { currentNim, findVoter } = useMockState()
  const [status, setStatus] = useState('idle') // idle | checking | valid | invalid
  const [attempts, setAttempts] = useState(0)

  const verifikasi = () => {
    setStatus('checking')
    setTimeout(() => setStatus('valid'), 1100)
  }

  const lanjut = () => {
    if (onValid) return onValid()
    const voter = findVoter(currentNim ?? '2141720001')
    navigate(voter?.hasVoted ? '/sudah-memilih' : '/booth')
  }

  const gagal = () => {
    setAttempts((a) => a + 1)
    setStatus('invalid')
  }

  const body = (
    <>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Verifikasi Wajah & Liveness</h2>
      <p className="text-sm text-slate-500 mb-6">Memastikan Anda adalah orang yang sama dengan data terdaftar (anti-spoofing aktif).</p>

      <div className="aspect-square w-full max-w-[360px] mx-auto rounded-2xl bg-slate-900 relative overflow-hidden flex items-center justify-center mb-5">
        <div className="absolute inset-8 border-2 border-dashed border-white/40 rounded-full" />
        {status === 'idle' && <span className="text-white/50 text-sm">Pratinjau kamera</span>}
        {status === 'checking' && <span className="text-white text-sm animate-pulse">Memeriksa liveness & kecocokan wajah…</span>}
        {status === 'valid' && <div className="text-7xl">✅</div>}
        {status === 'invalid' && <div className="text-7xl">🚫</div>}
      </div>

      {status === 'idle' && (
        <button onClick={verifikasi} className="w-full rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5">
          Mulai Verifikasi
        </button>
      )}

      {status === 'checking' && (
        <button disabled className="w-full rounded-lg bg-green-300 text-white font-semibold py-2.5">
          Memproses…
        </button>
      )}

      {status === 'valid' && (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-2 text-center">
            ✓ Valid — skor kecocokan 96.4%, liveness terkonfirmasi
          </p>
          <button onClick={lanjut} className="w-full rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5">
            Lanjutkan
          </button>
          <button onClick={gagal} className="text-xs text-slate-400 underline">
            (demo) simulasikan verifikasi gagal
          </button>
        </div>
      )}

      {status === 'invalid' && (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2 text-center">
            ✕ Tidak valid (percobaan ke-{attempts}/3). {attempts >= 3 ? 'Akun dikunci — hubungi panitia untuk verifikasi manual.' : 'Silakan coba lagi.'}
          </p>
          {attempts < 3 ? (
            <button onClick={() => setStatus('idle')} className="w-full rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5">
              Coba Lagi
            </button>
          ) : (
            <button disabled className="w-full rounded-lg bg-slate-300 text-white font-semibold py-2.5">
              Akun Terkunci
            </button>
          )}
        </div>
      )}
    </>
  )

  if (embedded) return <div>{body}</div>

  return <Screen width="max-w-lg">{body}</Screen>
}
