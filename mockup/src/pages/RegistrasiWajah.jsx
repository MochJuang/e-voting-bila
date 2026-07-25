import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

// Urutan pose enrollment: tengah, atas, kanan, bawah, kiri
const POSES = [
  { key: 'center', label: 'Tengah', instruksi: 'Hadapkan wajah lurus ke kamera', arrow: '●' },
  { key: 'up', label: 'Atas', instruksi: 'Dongakkan kepala sedikit ke atas', arrow: '↑' },
  { key: 'right', label: 'Kanan', instruksi: 'Tolehkan kepala ke kanan', arrow: '→' },
  { key: 'down', label: 'Bawah', instruksi: 'Tundukkan kepala sedikit ke bawah', arrow: '↓' },
  { key: 'left', label: 'Kiri', instruksi: 'Tolehkan kepala ke kiri', arrow: '←' },
]

// Frame abu-abu bertekstur untuk mode simulasi (tanpa kamera) agar backend fallback lolos kualitas.
function makeDummyFrame() {
  const canvas = document.createElement('canvas')
  canvas.width = 224
  canvas.height = 224
  const ctx = canvas.getContext('2d')
  const img = ctx.createImageData(224, 224)
  for (let i = 0; i < img.data.length; i += 4) {
    const v = 110 + Math.floor(Math.random() * 40)
    img.data[i] = img.data[i + 1] = img.data[i + 2] = v
    img.data[i + 3] = 255
  }
  ctx.putImageData(img, 0, 0)
  return canvas.toDataURL('image/jpeg')
}

export default function RegistrasiWajah() {
  const navigate = useNavigate()
  const { currentNim, findVoter, markFaceEnrolled } = useMockState()
  const voter = findVoter(currentNim)

  const [stepIndex, setStepIndex] = useState(0)
  const [captures, setCaptures] = useState({}) // { poseKey: dataURL }
  const [countdown, setCountdown] = useState(0)
  const [cameraReady, setCameraReady] = useState(false)
  const [cameraError, setCameraError] = useState(false)
  const [phase, setPhase] = useState('capture') // capture | review | saving | result
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)

  const currentPose = POSES[stepIndex]
  const allCaptured = POSES.every((p) => captures[p.key])

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

  const captureFrame = () => {
    if (cameraError || !cameraReady || !videoRef.current || !canvasRef.current) return makeDummyFrame()
    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width = video.videoWidth || 480
    canvas.height = video.videoHeight || 480
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
    return canvas.toDataURL('image/jpeg')
  }

  const capturePose = () => {
    // Hitung mundur 3..1 lalu ambil frame
    setCountdown(3)
    const tick = (n) => {
      if (n === 0) {
        const frame = captureFrame()
        setCaptures((prev) => ({ ...prev, [currentPose.key]: frame }))
        setCountdown(0)
        if (stepIndex < POSES.length - 1) {
          setStepIndex((i) => i + 1)
        } else {
          setPhase('review')
        }
        return
      }
      setCountdown(n)
      setTimeout(() => tick(n - 1), 700)
    }
    tick(3)
  }

  const ulangiPose = (key) => {
    const idx = POSES.findIndex((p) => p.key === key)
    setCaptures((prev) => {
      const next = { ...prev }
      delete next[key]
      return next
    })
    setStepIndex(idx)
    setPhase('capture')
  }

  const simpan = async () => {
    setPhase('saving')
    setError('')
    try {
      const frames = POSES.map((p) => ({ pose: p.key, imageBase64: captures[p.key] }))
      const res = await markFaceEnrolled(currentNim ?? '2141721001', frames)
      setResult(res)
      setPhase('result')
    } catch (err) {
      setError(err.message || 'Gagal menyimpan wajah.')
      setPhase('review')
    }
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
      <p className="text-sm text-slate-500 mb-4">
        Kami memindai wajah Anda dari <b>5 sudut</b> (tengah, atas, kanan, bawah, kiri) agar verifikasi lebih akurat.
      </p>

      {/* Progress 5 pose */}
      <div className="flex items-center justify-center gap-2 mb-4">
        {POSES.map((p, i) => {
          const done = Boolean(captures[p.key])
          const active = phase === 'capture' && i === stepIndex
          return (
            <div key={p.key} className="flex flex-col items-center gap-1">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold border-2 ${
                  done
                    ? 'bg-green-500 border-green-500 text-white'
                    : active
                      ? 'border-blue-500 text-blue-600 animate-pulse'
                      : 'border-slate-300 text-slate-400'
                }`}
              >
                {done ? '✓' : p.arrow}
              </div>
              <span className={`text-[10px] ${active ? 'text-blue-600 font-semibold' : 'text-slate-400'}`}>{p.label}</span>
            </div>
          )
        })}
      </div>

      {/* Kamera / preview */}
      <div className="aspect-square w-full max-w-[360px] mx-auto rounded-2xl bg-slate-900 relative overflow-hidden flex items-center justify-center mb-4">
        <div className="absolute inset-8 border-2 border-dashed border-white/40 rounded-full z-10 pointer-events-none" />
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className={`absolute inset-0 w-full h-full object-cover -scale-x-100 ${
            cameraReady && (phase === 'capture' || phase === 'review') ? 'block' : 'hidden'
          }`}
        />
        <canvas ref={canvasRef} className="hidden" />

        {!cameraReady && !cameraError && <span className="text-white/50 text-sm">Mengaktifkan kamera…</span>}
        {cameraError && <span className="text-white/50 text-sm text-center px-6">Kamera tidak tersedia — mode simulasi</span>}

        {countdown > 0 && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/30">
            <span className="text-white text-7xl font-bold">{countdown}</span>
          </div>
        )}

        {phase === 'capture' && countdown === 0 && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 bg-black/60 text-white text-xs px-3 py-1.5 rounded-full flex items-center gap-2">
            <span className="text-lg leading-none">{currentPose.arrow}</span>
            {currentPose.instruksi}
          </div>
        )}
      </div>

      {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2 mb-3 text-center">{error}</p>}

      {phase === 'capture' && (
        <button
          onClick={capturePose}
          disabled={countdown > 0}
          className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-2.5"
        >
          {countdown > 0 ? 'Bersiap…' : `Ambil Pose ${currentPose.label} (${stepIndex + 1}/5)`}
        </button>
      )}

      {phase === 'review' && (
        <div className="flex flex-col gap-3">
          <div className="grid grid-cols-5 gap-2">
            {POSES.map((p) => (
              <button
                key={p.key}
                onClick={() => ulangiPose(p.key)}
                title={`Ambil ulang ${p.label}`}
                className="group relative aspect-square rounded-lg overflow-hidden border border-slate-200"
              >
                <img src={captures[p.key]} alt={p.label} className="w-full h-full object-cover -scale-x-100" />
                <span className="absolute bottom-0 inset-x-0 bg-black/50 text-white text-[9px] py-0.5">{p.label}</span>
              </button>
            ))}
          </div>
          <p className="text-xs text-slate-400 text-center">Ketuk salah satu pose untuk mengambil ulang.</p>
          <button
            onClick={simpan}
            disabled={!allCaptured}
            className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-2.5"
          >
            Simpan &amp; Lanjutkan
          </button>
        </div>
      )}

      {phase === 'saving' && (
        <button disabled className="w-full rounded-lg bg-blue-300 text-white font-semibold py-2.5">
          Menyimpan 5 pose…
        </button>
      )}

      {phase === 'result' && result && (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-2 text-center">
            ✓ {result.message} {result.quality_score != null ? `(kualitas ${result.quality_score})` : ''}
          </p>
          {Array.isArray(result.poses) && (
            <ul className="text-xs text-slate-500 flex flex-col gap-1">
              {result.poses.map((p) => (
                <li key={p.pose} className="flex items-center gap-2">
                  <span className={p.accepted ? 'text-green-600' : 'text-amber-500'}>{p.accepted ? '✓' : '!'}</span>
                  <span className="font-medium capitalize">{p.pose}</span>
                  <span className="text-slate-400">— {p.message}</span>
                </li>
              ))}
            </ul>
          )}
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5"
          >
            Selesai
          </button>
        </div>
      )}
    </Screen>
  )
}
