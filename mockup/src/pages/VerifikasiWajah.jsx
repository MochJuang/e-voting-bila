import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

const SCAN_INTERVAL_MS = 700
const LIVENESS_TIMEOUT_MS = 20000

const CHALLENGE_META = {
  smile: { label: 'Tersenyum', icon: '😊', instruksi: 'Silakan TERSENYUM lebar' },
  blink: { label: 'Berkedip', icon: '😉', instruksi: 'Silakan BERKEDIP' },
  turn_left: { label: 'Hadap Kiri', icon: '⬅️', instruksi: 'Tolehkan kepala ke KIRI' },
  turn_right: { label: 'Hadap Kanan', icon: '➡️', instruksi: 'Tolehkan kepala ke KANAN' },
}

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

export default function VerifikasiWajah({ onValid, embedded = false }) {
  const navigate = useNavigate()
  const { currentNim, findVoter, verifyFace } = useMockState()
  const nim = currentNim ?? '2141721001'

  const [phase, setPhase] = useState('scanning') // scanning | liveness | success | invalid | locked
  const [challenge, setChallenge] = useState(null)
  const [similarity, setSimilarity] = useState(null)
  const [message, setMessage] = useState('')
  const [attempts, setAttempts] = useState(0)
  const [cameraError, setCameraError] = useState(false)

  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)

  // Refs untuk loop agar tidak terkena stale closure
  const verifyRef = useRef(verifyFace)
  verifyRef.current = verifyFace
  const nimRef = useRef(nim)
  nimRef.current = nim
  const phaseRef = useRef('scanning')
  const challengeRef = useRef(null)
  const stoppedRef = useRef(false)
  const busyRef = useRef(false)
  const cameraErrorRef = useRef(false)
  const timerRef = useRef(null)
  const livenessTimerRef = useRef(null)
  const pumpRef = useRef(null)

  const captureFrame = () => {
    if (cameraErrorRef.current) return makeDummyFrame()
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas || !video.videoWidth) return null
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
    return canvas.toDataURL('image/jpeg')
  }

  const clearTimers = () => {
    if (timerRef.current) clearTimeout(timerRef.current)
    if (livenessTimerRef.current) clearTimeout(livenessTimerRef.current)
    timerRef.current = null
    livenessTimerRef.current = null
  }

  const stopStream = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
  }

  const toSuccess = (res) => {
    stoppedRef.current = true
    clearTimers()
    stopStream()
    setPhase('success')
    setMessage(res?.message || 'Verifikasi berhasil.')
  }

  const toLocked = () => {
    stoppedRef.current = true
    clearTimers()
    stopStream()
    setPhase('locked')
  }

  const toInvalid = (msg) => {
    stoppedRef.current = true
    clearTimers()
    setPhase('invalid')
    setMessage(msg || 'Verifikasi gagal.')
  }

  const startLivenessTimeout = () => {
    if (livenessTimerRef.current) clearTimeout(livenessTimerRef.current)
    livenessTimerRef.current = setTimeout(async () => {
      stoppedRef.current = true
      if (timerRef.current) clearTimeout(timerRef.current)
      try {
        const frame = captureFrame() || makeDummyFrame()
        const res = await verifyRef.current({
          nim: nimRef.current,
          imageBase64: frame,
          stage: 'liveness',
          challenge: challengeRef.current,
          timedOut: true,
        })
        setAttempts(res.retry_count ?? 0)
        if (res.lock_applied) toLocked()
        else toInvalid(res.message || 'Waktu liveness habis.')
      } catch (err) {
        toInvalid(err.message || 'Waktu liveness habis.')
      }
    }, LIVENESS_TIMEOUT_MS)
  }

  const schedule = () => {
    timerRef.current = setTimeout(() => pumpRef.current?.(), SCAN_INTERVAL_MS)
  }

  const pump = async () => {
    if (stoppedRef.current) return
    if (busyRef.current) return schedule()
    const frame = captureFrame()
    if (!frame) return schedule()

    busyRef.current = true
    try {
      if (phaseRef.current === 'scanning') {
        const res = await verifyRef.current({ nim: nimRef.current, imageBase64: frame, stage: 'match' })
        setSimilarity(res.similarity_score ?? null)
        setAttempts(res.retry_count ?? 0)
        if (res.lock_applied) return toLocked()
        if (res.matched && res.challenge) {
          challengeRef.current = res.challenge
          setChallenge(res.challenge)
          phaseRef.current = 'liveness'
          setPhase('liveness')
          setMessage('')
          startLivenessTimeout()
        } else {
          setMessage(res.message || 'Mencari kecocokan wajah…')
        }
      } else if (phaseRef.current === 'liveness') {
        const res = await verifyRef.current({
          nim: nimRef.current,
          imageBase64: frame,
          stage: 'liveness',
          challenge: challengeRef.current,
        })
        setSimilarity(res.similarity_score ?? null)
        if (res.verified) return toSuccess(res)
        if (res.lock_applied) return toLocked()
        setMessage(res.message || '')
      }
    } catch (err) {
      setMessage(err.message || 'Gagal terhubung ke server verifikasi.')
    } finally {
      busyRef.current = false
    }
    if (!stoppedRef.current) schedule()
  }
  pumpRef.current = pump

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
      })
      .catch(() => {
        cameraErrorRef.current = true
        setCameraError(true)
      })

    // Mulai loop; captureFrame otomatis menunggu video siap / pakai dummy jika kamera gagal
    stoppedRef.current = false
    schedule()

    return () => {
      cancelled = true
      stoppedRef.current = true
      clearTimers()
      stopStream()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const restart = () => {
    setMessage('')
    setChallenge(null)
    setSimilarity(null)
    challengeRef.current = null
    phaseRef.current = 'scanning'
    setPhase('scanning')
    busyRef.current = false
    stoppedRef.current = false
    schedule()
  }

  const lanjut = () => {
    if (onValid) return onValid()
    const voter = findVoter(nim)
    navigate(voter?.hasVoted ? '/sudah-memilih' : '/booth')
  }

  const challengeInfo = challenge ? CHALLENGE_META[challenge] : null
  const showVideo = phase === 'scanning' || phase === 'liveness'

  const body = (
    <>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Verifikasi Wajah &amp; Liveness</h2>
      <p className="text-sm text-slate-500 mb-4">
        Pemindaian berjalan otomatis (realtime). Posisikan wajah — sistem mencocokkan lalu meminta satu gerakan acak.
      </p>

      <div className="aspect-square w-full max-w-[360px] mx-auto rounded-2xl bg-slate-900 relative overflow-hidden flex items-center justify-center mb-4">
        <div
          className={`absolute inset-8 border-2 rounded-full z-10 pointer-events-none ${
            phase === 'liveness' ? 'border-amber-400 border-solid' : 'border-white/40 border-dashed'
          }`}
        />
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className={`absolute inset-0 w-full h-full object-cover -scale-x-100 ${showVideo ? 'block' : 'hidden'}`}
        />
        <canvas ref={canvasRef} className="hidden" />

        {cameraError && showVideo && (
          <span className="text-white/50 text-sm text-center px-6 z-20">Kamera tidak tersedia — mode simulasi</span>
        )}

        {phase === 'scanning' && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 bg-black/60 text-white text-xs px-3 py-1.5 rounded-full flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Memindai &amp; mencocokkan…
          </div>
        )}

        {phase === 'liveness' && challengeInfo && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20 bg-amber-500 text-white text-sm font-semibold px-4 py-2 rounded-full flex items-center gap-2 shadow-lg">
            <span className="text-lg leading-none">{challengeInfo.icon}</span>
            {challengeInfo.instruksi}
          </div>
        )}

        {phase === 'success' && <div className="text-6xl z-20">✅</div>}
        {phase === 'invalid' && <div className="text-6xl z-20">⚠️</div>}
        {phase === 'locked' && <div className="text-6xl z-20">🔒</div>}
      </div>

      {/* Indikator similarity */}
      {(phase === 'scanning' || phase === 'liveness') && similarity != null && (
        <div className="mb-3">
          <div className="flex justify-between text-[11px] text-slate-400 mb-1">
            <span>Kecocokan wajah</span>
            <span>{Math.round(similarity * 100)}%</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-slate-200 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${phase === 'liveness' ? 'bg-amber-400' : 'bg-green-500'}`}
              style={{ width: `${Math.min(100, Math.round(similarity * 100))}%` }}
            />
          </div>
        </div>
      )}

      {message && (phase === 'scanning' || phase === 'liveness') && (
        <p className="text-xs text-slate-500 text-center mb-3">{message}</p>
      )}

      {phase === 'success' && (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-2 text-center">✓ {message}</p>
          <button onClick={lanjut} className="w-full rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5">
            Lanjutkan
          </button>
        </div>
      )}

      {phase === 'invalid' && (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2 text-center">
            {message} {attempts > 0 ? `(percobaan ${attempts}/3)` : ''}
          </p>
          <button onClick={restart} className="w-full rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5">
            Coba Lagi
          </button>
        </div>
      )}

      {phase === 'locked' && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2 text-center">
          🔒 Akun dikunci sementara setelah beberapa percobaan gagal. Hubungi panitia untuk verifikasi manual.
        </p>
      )}
    </>
  )

  if (embedded) return <div>{body}</div>
  return <Screen width="max-w-lg">{body}</Screen>
}
