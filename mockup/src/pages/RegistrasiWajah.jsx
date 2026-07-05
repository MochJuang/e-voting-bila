import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

const PANDUAN = [
  'Pastikan pencahayaan cukup, hindari cahaya dari belakang',
  'Lepas kacamata hitam, masker, atau penutup wajah lain',
  'Posisikan wajah tepat di tengah bingkai',
]

export default function RegistrasiWajah() {
  const navigate = useNavigate()
  const { currentNim, findVoter, markFaceEnrolled } = useMockState()
  const voter = findVoter(currentNim)

  const [status, setStatus] = useState('idle') // idle | capturing | detected | not-detected
  const [attempt, setAttempt] = useState(0)
  const [cameraReady, setCameraReady] = useState(false)
  const [cameraError, setCameraError] = useState(false)
  const [capturedFrame, setCapturedFrame] = useState(null)

  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    navigator.mediaDevices
      ?.getUserMedia({ video: { facingMode: 'user' } })
      .then((stream) => {
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop())
          return
        }
        streamRef.current = stream
        if (videoRef.current) videoRef.current.srcObject = stream
        setCameraReady(true)
      })
      .catch(() => setCameraError(true))

    return () => {
      cancelled = true
      streamRef.current?.getTracks().forEach((t) => t.stop())
    }
  }, [])

  const ambilFoto = () => {
    setStatus('capturing')

    if (cameraReady && videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      canvas.getContext('2d').drawImage(video, 0, 0)
      setCapturedFrame(canvas.toDataURL('image/jpeg'))
    }

    setTimeout(() => {
      setAttempt((a) => a + 1)
      setStatus('detected')
    }, 900)
  }

  const ambilUlang = () => {
    setCapturedFrame(null)
    setStatus('idle')
  }

  const lanjut = () => {
    markFaceEnrolled(currentNim ?? '2141720001', capturedFrame)
    navigate('/dashboard')
  }

  return (
    <Screen width="max-w-lg">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-xl font-bold text-slate-900">Registrasi Wajah</h2>
        <Link to="/dashboard" className="text-xs font-medium text-slate-400 hover:text-slate-600">
          ← Kembali
        </Link>
      </div>
      {voter && (
        <p className="text-xs text-slate-400 font-mono mb-3">
          {voter.nim} — {voter.nama}
        </p>
      )}
      <p className="text-sm text-slate-500 mb-4">Ambil foto wajah untuk didaftarkan sebagai referensi verifikasi biometrik Anda.</p>

      <ul className="mb-4 flex flex-col gap-1.5">
        {PANDUAN.map((p) => (
          <li key={p} className="flex items-start gap-2 text-xs text-slate-500">
            <span className="text-blue-500 mt-0.5">•</span>
            <span>{p}</span>
          </li>
        ))}
      </ul>

      <div className="aspect-square w-full max-w-[360px] mx-auto rounded-2xl bg-slate-900 relative overflow-hidden flex items-center justify-center mb-4">
        <div className="absolute inset-8 border-2 border-dashed border-white/40 rounded-full z-10 pointer-events-none" />

        {/* Live camera feed (hidden once a frame is captured or if permission denied) */}
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className={`absolute inset-0 w-full h-full object-cover -scale-x-100 ${
            cameraReady && status !== 'detected' && status !== 'not-detected' ? 'block' : 'hidden'
          }`}
        />
        <canvas ref={canvasRef} className="hidden" />

        {!cameraReady && !cameraError && status === 'idle' && <span className="text-white/50 text-sm">Mengaktifkan kamera…</span>}
        {cameraError && status === 'idle' && (
          <span className="text-white/50 text-sm text-center px-6">Kamera tidak tersedia — mode simulasi digunakan</span>
        )}
        {status === 'capturing' && <span className="text-white text-sm animate-pulse">Mengambil gambar…</span>}

        {(status === 'detected' || status === 'not-detected') &&
          (capturedFrame ? (
            <img src={capturedFrame} alt="Hasil capture wajah" className="w-full h-full object-cover -scale-x-100" />
          ) : (
            <div className="text-6xl">{status === 'detected' ? '🙂' : '❔'}</div>
          ))}
      </div>

      {status === 'not-detected' && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2 mb-3 text-center">
          Wajah tidak terdeteksi (kode C). Coba lagi dengan pencahayaan lebih baik.
        </p>
      )}

      {status === 'idle' && (
        <button onClick={ambilFoto} className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5">
          Ambil Foto
        </button>
      )}

      {status === 'capturing' && (
        <button disabled className="w-full rounded-lg bg-blue-300 text-white font-semibold py-2.5">
          Memproses…
        </button>
      )}

      {status === 'detected' && (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-2 text-center">
            ✓ Wajah terdeteksi dengan kualitas baik {attempt > 1 ? `(percobaan ke-${attempt})` : ''}
          </p>
          <button onClick={lanjut} className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5">
            Simpan &amp; Lanjutkan
          </button>
          <button onClick={ambilUlang} className="w-full rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50 text-sm font-medium py-2">
            Ambil Ulang
          </button>
          <button onClick={() => setStatus('not-detected')} className="text-xs text-slate-400 underline">
            (demo) simulasikan wajah tidak terdeteksi
          </button>
        </div>
      )}

      {status === 'not-detected' && (
        <button onClick={ambilUlang} className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5">
          Ambil Ulang Foto
        </button>
      )}
    </Screen>
  )
}
