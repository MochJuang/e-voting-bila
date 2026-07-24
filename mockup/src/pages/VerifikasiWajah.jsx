import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

const DUMMY_FRAME =
  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8E2S8AAAAASUVORK5CYII='

export default function VerifikasiWajah({ onValid, embedded = false }) {
  const navigate = useNavigate()
  const { currentNim, findVoter, verifyFace } = useMockState()
  const [status, setStatus] = useState('idle')
  const [attempts, setAttempts] = useState(0)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [cameraReady, setCameraReady] = useState(false)
  const [cameraError, setCameraError] = useState(false)
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    navigator.mediaDevices
      ?.getUserMedia({ video: { facingMode: 'user' } })
      .then((stream) => {
        if (cancelled) {
          stream.getTracks().forEach((track) => track.stop())
          return
        }
        streamRef.current = stream
        if (videoRef.current) videoRef.current.srcObject = stream
        setCameraReady(true)
      })
      .catch(() => setCameraError(true))

    return () => {
      cancelled = true
      streamRef.current?.getTracks().forEach((track) => track.stop())
    }
  }, [])

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return null
    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width = video.videoWidth || 640
    canvas.height = video.videoHeight || 480
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
    return canvas.toDataURL('image/jpeg')
  }

  const verifikasi = async () => {
    setLoading(true)
    setStatus('checking')
    setMessage('')
    try {
      const frame = captureFrame() || DUMMY_FRAME
      const result = await verifyFace({ nim: currentNim ?? '2141720001', imageBase64: frame })
      if (result.verified) {
        setStatus('valid')
        setMessage(result.message || 'Verifikasi wajah berhasil.')
      } else {
        setAttempts((a) => a + 1)
        setStatus('invalid')
        setMessage(result.message || 'Verifikasi gagal.')
      }
    } catch (err) {
      setAttempts((a) => a + 1)
      setStatus('invalid')
      setMessage(err.message || 'Verifikasi gagal.')
    } finally {
      setLoading(false)
    }
  }

  const lanjut = () => {
    if (onValid) return onValid()
    const voter = findVoter(currentNim ?? '2141720001')
    navigate(voter?.hasVoted ? '/sudah-memilih' : '/booth')
  }

  const reset = () => {
    setMessage('')
    setStatus('idle')
  }

  const body = (
    <>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Verifikasi Wajah & Liveness</h2>
      <p className="text-sm text-slate-500 mb-6">Memastikan Anda adalah orang yang sama dengan data terdaftar (anti-spoofing aktif).</p>

      <div className="aspect-square w-full max-w-[360px] mx-auto rounded-2xl bg-slate-900 relative overflow-hidden flex items-center justify-center mb-5">
        <div className="absolute inset-8 border-2 border-dashed border-white/40 rounded-full" />
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className={`absolute inset-0 w-full h-full object-cover -scale-x-100 ${
            cameraReady && status !== 'valid' && status !== 'invalid' ? 'block' : 'hidden'
          }`}
        />
        <canvas ref={canvasRef} className="hidden" />
        {status === 'idle' && <span className="text-white/50 text-sm">{cameraError ? 'Kamera tidak tersedia' : 'Pratinjau kamera'}</span>}
        {status === 'checking' && <span className="text-white text-sm animate-pulse">Memeriksa liveness dan kecocokan wajah...</span>}
        {status === 'valid' && <div className="text-7xl">OK</div>}
        {status === 'invalid' && <div className="text-7xl">NO</div>}
      </div>

      {status === 'idle' && (
        <button onClick={verifikasi} disabled={loading} className="w-full rounded-lg bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white font-semibold py-2.5">
          {cameraError ? 'Verifikasi Simulasi' : 'Mulai Verifikasi'}
        </button>
      )}

      {status === 'checking' && (
        <button disabled className="w-full rounded-lg bg-green-300 text-white font-semibold py-2.5">
          Memproses...
        </button>
      )}

      {status === 'valid' && (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg p-2 text-center">
            Valid - {message}
          </p>
          <button onClick={lanjut} className="w-full rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5">
            Lanjutkan
          </button>
          <button onClick={reset} className="text-xs text-slate-400 underline">
            (demo) simulasikan verifikasi gagal
          </button>
        </div>
      )}

      {status === 'invalid' && (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2 text-center">
            Tidak valid (percobaan ke-{attempts}/3). {attempts >= 3 ? 'Akun dikunci - hubungi panitia untuk verifikasi manual.' : message}
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
