import { useNavigate, Link } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

export default function MahasiswaDashboard() {
  const navigate = useNavigate()
  const { currentNim, currentUser, findVoter, logoutStudent } = useMockState()
  const voter = currentUser || findVoter(currentNim) || findVoter('2141720001')

  const isAssisted = voter?.modeAkses === 'admin_assisted'

  const logout = () => {
    logoutStudent()
    navigate('/')
  }

  return (
    <Screen width="max-w-lg">
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-xs text-slate-400">Selamat datang,</p>
          <h2 className="text-lg font-bold text-slate-900">{voter?.nama}</h2>
          <p className="text-xs text-slate-500 font-mono">{voter?.nim}</p>
        </div>
        <span
          className={`text-xs rounded-full px-2.5 py-1 font-medium ${
            isAssisted ? 'bg-purple-50 text-purple-700' : 'bg-blue-50 text-blue-700'
          }`}
        >
          {isAssisted ? 'Admin-Assisted' : 'Mandiri'}
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {/* Registrasi */}
        <div className="rounded-xl border border-slate-200 p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="font-semibold text-slate-900 text-sm">Registrasi Wajah</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {voter?.faceEnrolled ? 'Wajah Anda sudah terdaftar di sistem.' : 'Anda belum mendaftarkan wajah. Wajib dilakukan sebelum memilih.'}
              </p>
            </div>
            <span className={`shrink-0 text-xs rounded-full px-2 py-0.5 ${voter?.faceEnrolled ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
              {voter?.faceEnrolled ? '✓ Terdaftar' : 'Belum'}
            </span>
          </div>
          <button
            onClick={() => navigate('/registrasi-wajah')}
            className="mt-3 w-full rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold py-2"
          >
            {voter?.faceEnrolled ? 'Update Ulang Wajah' : 'Mulai Registrasi Wajah'}
          </button>
        </div>

        {/* Pemilihan */}
        <div className={`rounded-xl border p-4 ${isAssisted ? 'border-slate-200 bg-slate-50' : 'border-slate-200'}`}>
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="font-semibold text-slate-900 text-sm">Pemilihan</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {isAssisted
                  ? 'Mode akses Anda "Admin-Assisted" — pemungutan suara wajib dilakukan di kiosk panitia, tidak bisa lewat halaman ini.'
                  : voter?.hasVoted
                  ? 'Anda sudah menyelesaikan pemungutan suara pada sesi ini.'
                  : 'Berikan suara Anda untuk seluruh jabatan yang dibuka.'}
              </p>
            </div>
            <span
              className={`shrink-0 text-xs rounded-full px-2 py-0.5 ${
                voter?.hasVoted ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-500'
              }`}
            >
              {voter?.hasVoted ? '✓ Sudah Memilih' : 'Belum'}
            </span>
          </div>
          <button
            disabled={isAssisted || voter?.hasVoted}
            onClick={() => navigate('/verifikasi-wajah')}
            className="mt-3 w-full rounded-lg bg-purple-600 hover:bg-purple-700 disabled:bg-slate-200 disabled:text-slate-400 text-white text-sm font-semibold py-2"
          >
            {isAssisted ? 'Kunjungi Kiosk Panitia' : voter?.hasVoted ? 'Sudah Memilih' : 'Mulai Verifikasi & Pilih'}
          </button>
        </div>

        {/* Reset Password */}
        <div className="rounded-xl border border-slate-200 p-4">
          <p className="font-semibold text-slate-900 text-sm">Keamanan Akun</p>
          <p className="text-xs text-slate-500 mt-0.5">Lupa atau ingin mengganti password akun Anda?</p>
          <Link
            to="/reset-password"
            className="mt-3 block text-center w-full rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-semibold py-2"
          >
            Reset Password
          </Link>
        </div>
      </div>

      <button onClick={logout} className="mt-5 w-full text-center text-sm text-slate-400 hover:text-slate-600">
        Keluar
      </button>
    </Screen>
  )
}
