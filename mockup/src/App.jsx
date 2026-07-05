import { Routes, Route } from 'react-router-dom'
import { MockStateProvider } from './context/MockStateContext'
import DevNav from './components/DevNav'

import Home from './pages/Home'
import Daftar from './pages/Daftar'
import Login from './pages/Login'
import MahasiswaDashboard from './pages/MahasiswaDashboard'
import ResetPassword from './pages/ResetPassword'
import RegistrasiWajah from './pages/RegistrasiWajah'
import VerifikasiWajah from './pages/VerifikasiWajah'
import Booth from './pages/Booth'
import SudahMemilih from './pages/SudahMemilih'
import Selesai from './pages/Selesai'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'
import AdminKiosk from './pages/AdminKiosk'
import AdminRekapitulasi from './pages/AdminRekapitulasi'
import AdminKandidat from './pages/AdminKandidat'
import AdminMahasiswa from './pages/AdminMahasiswa'

function App() {
  return (
    <MockStateProvider>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/daftar" element={<Daftar />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<MahasiswaDashboard />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/registrasi-wajah" element={<RegistrasiWajah />} />
        <Route path="/verifikasi-wajah" element={<VerifikasiWajah />} />
        <Route path="/booth" element={<Booth />} />
        <Route path="/sudah-memilih" element={<SudahMemilih />} />
        <Route path="/selesai" element={<Selesai />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/kiosk" element={<AdminKiosk />} />
        <Route path="/admin/rekapitulasi" element={<AdminRekapitulasi />} />
        <Route path="/admin/kandidat" element={<AdminKandidat />} />
        <Route path="/admin/mahasiswa" element={<AdminMahasiswa />} />
      </Routes>
      <DevNav />
    </MockStateProvider>
  )
}

export default App
