import { useState } from 'react'
import { Link } from 'react-router-dom'
import Screen from '../components/Screen'
import VerifikasiWajah from './VerifikasiWajah'
import Booth from './Booth'
import SudahMemilih from './SudahMemilih'
import Selesai from './Selesai'
import { useMockState } from '../context/MockStateContext'

export default function AdminKiosk() {
  const { findVoter, setCurrentNim } = useMockState()
  const [step, setStep] = useState('input-nim')
  const [nim, setNim] = useState('')
  const [error, setError] = useState('')
  const [voterName, setVoterName] = useState('')

  const resetToInput = () => {
    setStep('input-nim')
    setNim('')
    setError('')
    setVoterName('')
  }

  const handleLookup = (e) => {
    e.preventDefault()
    const voter = findVoter(nim)
    if (!voter) {
      setError('NIM tidak ditemukan di Daftar Pemilih Tetap.')
      return
    }
    if (voter.modeAkses !== 'admin_assisted') {
      setError('NIM ini berstatus "Mandiri" — arahkan mahasiswa untuk login sendiri (NIM & password), tidak perlu kiosk.')
      return
    }
    setError('')
    setVoterName(voter.nama)
    setCurrentNim(nim)
    setStep(voter.hasVoted ? 'sudah-memilih' : 'verifikasi')
  }

  return (
    <div className="min-h-svh flex flex-col">
      <div className="bg-purple-700 text-white text-sm px-4 py-2 flex items-center justify-between">
        <span>
          🖥 Kiosk Terdaftar: <b>Komputer Panitia #1</b> · Login sebagai <b>admin (panitia1)</b>
        </span>
        <Link to="/admin/dashboard" className="underline text-purple-100">
          Keluar Kiosk
        </Link>
      </div>

      <Screen width={step === 'booth' ? 'max-w-xl' : 'max-w-md'}>
        {step === 'input-nim' && (
          <>
            <h2 className="text-lg font-bold text-slate-900 mb-1">Mode Admin-Assisted</h2>
            <p className="text-sm text-slate-500 mb-5">
              Untuk mahasiswa yang belum punya password/akun lengkap. Mahasiswa memasukkan NIM-nya sendiri, lalu tetap
              melalui verifikasi wajah &amp; memilih sendiri.
            </p>
            <form onSubmit={handleLookup} className="flex flex-col gap-3">
              <label className="block text-left">
                <span className="text-xs font-medium text-slate-600">NIM Mahasiswa</span>
                <input
                  autoFocus
                  value={nim}
                  onChange={(e) => setNim(e.target.value)}
                  placeholder="Masukkan NIM"
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400"
                />
              </label>
              {error && <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
              <button type="submit" className="mt-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2.5">
                Lanjutkan
              </button>
            </form>
            <div className="mt-4 text-xs text-slate-400 bg-slate-50 border border-slate-200 rounded-lg p-2">
              Coba NIM: <b>2141720003</b> (admin-assisted, belum memilih) · <b>2141720004</b> (admin-assisted, wajah belum enroll)
            </div>
          </>
        )}

        {step === 'sudah-memilih' && (
          <>
            <p className="text-xs text-slate-400 mb-2">NIM {nim} — {voterName}</p>
            <SudahMemilih embedded />
            <button onClick={resetToInput} className="w-full mt-4 rounded-lg bg-slate-900 text-white font-semibold py-2.5 text-sm">
              Sesi Berikutnya
            </button>
          </>
        )}

        {step === 'verifikasi' && (
          <>
            <p className="text-xs text-slate-400 mb-2">NIM {nim} — {voterName}</p>
            <VerifikasiWajah embedded onValid={() => setStep('booth')} />
          </>
        )}

        {step === 'booth' && (
          <>
            <p className="text-xs text-slate-400 mb-2">NIM {nim} — {voterName}</p>
            <Booth embedded onSubmitted={() => setStep('selesai')} />
          </>
        )}

        {step === 'selesai' && (
          <>
            <p className="text-xs text-slate-400 mb-2">NIM {nim} — {voterName}</p>
            <Selesai embedded />
            <button onClick={resetToInput} className="w-full mt-4 rounded-lg bg-slate-900 text-white font-semibold py-2.5 text-sm">
              Sesi Berikutnya
            </button>
          </>
        )}
      </Screen>
    </div>
  )
}
