import { createContext, useContext, useState } from 'react'
import { MOCK_DPT, JABATAN } from '../data/mockData'

const MockStateContext = createContext(null)

let idCounter = 1000
const nextId = (prefix) => `${prefix}-${idCounter++}`

export function MockStateProvider({ children }) {
  const [dpt, setDpt] = useState(MOCK_DPT)
  const [jabatan, setJabatan] = useState(JABATAN)
  const [currentNim, setCurrentNim] = useState(null)
  const [votes, setVotes] = useState({})

  const findVoter = (nim) => dpt.find((v) => v.nim === nim)

  const markFaceEnrolled = (nim, fotoWajah) => {
    setDpt((prev) =>
      prev.map((v) => (v.nim === nim ? { ...v, faceEnrolled: true, ...(fotoWajah ? { fotoWajah } : {}) } : v)),
    )
  }

  const markVoted = (nim) => {
    setDpt((prev) => prev.map((v) => (v.nim === nim ? { ...v, hasVoted: true } : v)))
  }

  const submitVotes = (nim, selections) => {
    setVotes((prev) => {
      const next = { ...prev }
      Object.entries(selections).forEach(([jabatanId, kandidatId]) => {
        next[jabatanId] = next[jabatanId] || {}
        next[jabatanId][kandidatId] = (next[jabatanId][kandidatId] || 0) + 1
      })
      return next
    })
    markVoted(nim)
  }

  // --- Manajemen Data Mahasiswa (DPT) ---
  const addVoter = (voter) => {
    setDpt((prev) => [
      ...prev,
      { hasVoted: false, faceEnrolled: false, modeAkses: 'mandiri', ...voter },
    ])
  }

  const updateVoter = (nim, patch) => {
    setDpt((prev) => prev.map((v) => (v.nim === nim ? { ...v, ...patch } : v)))
  }

  const deleteVoter = (nim) => {
    setDpt((prev) => prev.filter((v) => v.nim !== nim))
  }

  // --- Manajemen Data Kandidat & Jabatan ---
  const addJabatan = (nama) => {
    setJabatan((prev) => [...prev, { id: nextId('jbt'), nama, kandidat: [] }])
  }

  const updateJabatan = (jabatanId, patch) => {
    setJabatan((prev) => prev.map((j) => (j.id === jabatanId ? { ...j, ...patch } : j)))
  }

  const deleteJabatan = (jabatanId) => {
    setJabatan((prev) => prev.filter((j) => j.id !== jabatanId))
  }

  const addKandidat = (jabatanId, kandidat) => {
    setJabatan((prev) =>
      prev.map((j) =>
        j.id === jabatanId ? { ...j, kandidat: [...j.kandidat, { id: nextId('kdd'), ...kandidat }] } : j,
      ),
    )
  }

  const updateKandidat = (jabatanId, kandidatId, patch) => {
    setJabatan((prev) =>
      prev.map((j) =>
        j.id === jabatanId
          ? { ...j, kandidat: j.kandidat.map((k) => (k.id === kandidatId ? { ...k, ...patch } : k)) }
          : j,
      ),
    )
  }

  const deleteKandidat = (jabatanId, kandidatId) => {
    setJabatan((prev) =>
      prev.map((j) => (j.id === jabatanId ? { ...j, kandidat: j.kandidat.filter((k) => k.id !== kandidatId) } : j)),
    )
  }

  const value = {
    dpt,
    findVoter,
    markFaceEnrolled,
    markVoted,
    currentNim,
    setCurrentNim,
    votes,
    submitVotes,
    addVoter,
    updateVoter,
    deleteVoter,
    jabatan,
    addJabatan,
    updateJabatan,
    deleteJabatan,
    addKandidat,
    updateKandidat,
    deleteKandidat,
  }

  return <MockStateContext.Provider value={value}>{children}</MockStateContext.Provider>
}

export function useMockState() {
  const ctx = useContext(MockStateContext)
  if (!ctx) throw new Error('useMockState must be used within MockStateProvider')
  return ctx
}
