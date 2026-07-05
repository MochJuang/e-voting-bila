import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Screen from '../components/Screen'
import { useMockState } from '../context/MockStateContext'

export default function Daftar() {
  const navigate = useNavigate()
  const { findVoter, addVoter, setCurrentNim } = useMockState()
  const [form, setForm] = useState({ nim: '', nama: '', email: '', password: '' })

  return (
    <Screen>
      <h2 className="text-xl font-bold text-slate-900 mb-1">Daftar Akun Mahasiswa</h2>
      <p className="text-sm text-slate-500 mb-5">NIM Anda akan dicocokkan dengan Daftar Pemilih Tetap (DPT).</p>

      <form
        className="flex flex-col gap-3"
        onSubmit={(e) => {
          e.preventDefault()
          if (!findVoter(form.nim)) addVoter({ nim: form.nim, nama: form.nama })
          setCurrentNim(form.nim)
          navigate('/registrasi-wajah')
        }}
      >
        <Field label="NIM" placeholder="2141720001" value={form.nim} onChange={(v) => setForm({ ...form, nim: v })} />
        <Field label="Nama Lengkap" placeholder="Nama sesuai KTM" value={form.nama} onChange={(v) => setForm({ ...form, nama: v })} />
        <Field label="Email Kampus" type="email" placeholder="nama@kampus.ac.id" value={form.email} onChange={(v) => setForm({ ...form, email: v })} />
        <Field label="Password" type="password" placeholder="Minimal 8 karakter" value={form.password} onChange={(v) => setForm({ ...form, password: v })} />

        <button type="submit" className="mt-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5">
          Daftar & Lanjut Registrasi Wajah
        </button>
      </form>

      <p className="text-center text-sm text-slate-500 mt-4">
        Sudah punya akun? <Link to="/login" className="text-blue-600 font-medium">Login</Link>
      </p>
    </Screen>
  )
}

function Field({ label, value, onChange, type = 'text', placeholder }) {
  return (
    <label className="block text-left">
      <span className="text-xs font-medium text-slate-600">{label}</span>
      <input
        type={type}
        required
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
    </label>
  )
}
