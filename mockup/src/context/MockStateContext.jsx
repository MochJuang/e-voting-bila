import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { MOCK_DPT, JABATAN } from '../data/mockData'
import { api, clearAdminToken, clearStudentToken, getAdminToken, getStudentToken, setAdminToken, setStudentToken } from '../lib/api'

const MockStateContext = createContext(null)

const cloneJson = (value) => JSON.parse(JSON.stringify(value))

function normalizeVoter(user) {
  return {
    id: user.id,
    nim: user.nim,
    nama: user.nama,
    email: user.email ?? '',
    kelas: user.kelas ?? '-',
    modeAkses: user.mode_akses ?? 'mandiri',
    hasVoted: Boolean(user.has_voted),
    faceEnrolled: Boolean(user.face_enrolled),
    isLocked: Boolean(user.is_locked),
    isDptMember: user.is_dpt_member ?? true,
    faceNote: user.face_note ?? null,
    fotoWajah: user.fotoWajah ?? null,
  }
}

function normalizePosition(position) {
  return {
    id: position.id,
    nama: position.name ?? position.nama,
    kandidat: (position.candidates ?? position.kandidat ?? []).map((candidate) => ({
      id: candidate.id,
      nama: candidate.name ?? candidate.nama,
      nomor: candidate.number ?? candidate.nomor,
      warna: candidate.color ?? candidate.warna ?? '#2563eb',
      visi: candidate.vision ?? candidate.visi ?? '',
    })),
  }
}

function votesFromResults(results = []) {
  const mapped = {}
  results.forEach((position) => {
    const counts = {}
    ;(position.results || []).forEach((candidate) => {
      counts[candidate.candidate_id] = candidate.votes
    })
    mapped[position.position_id] = counts
  })
  return mapped
}

function positionsFromSession(session) {
  if (!session?.positions) return []
  return session.positions.map((position) => normalizePosition(position))
}

export function MockStateProvider({ children }) {
  const [dpt, setDpt] = useState(cloneJson(MOCK_DPT))
  const [jabatan, setJabatan] = useState(cloneJson(JABATAN))
  const [currentNim, setCurrentNim] = useState(null)
  const [currentUser, setCurrentUser] = useState(null)
  const [studentToken, setStudentTokenState] = useState(() => getStudentToken())
  const [adminToken, setAdminTokenState] = useState(() => getAdminToken())
  const [session, setSession] = useState(null)
  const [votes, setVotes] = useState({})
  const [loading, setLoading] = useState(false)
  const [verificationToken, setVerificationToken] = useState(null)
  const [lastVoteReference, setLastVoteReference] = useState(null)

  const isOnlineMode = useMemo(() => Boolean(import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'), [])

  const syncVoterList = (users) => {
    const normalized = users.map(normalizeVoter)
    setDpt(normalized)
    return normalized
  }

  const syncPositions = (positions) => {
    const normalized = positions.map(normalizePosition)
    setJabatan(normalized)
    return normalized
  }

  const syncResults = (resultsResponse) => {
    setVotes(votesFromResults(resultsResponse.positions || []))
  }

  const refreshStudentSnapshot = async (token = studentToken) => {
    if (!token) return null
    const [me, status, active] = await Promise.all([
      api.auth.me(token),
      api.voters.status(token),
      api.election.active().catch(() => null),
    ])
    setCurrentUser(me)
    setCurrentNim(me.nim)
    const voter = normalizeVoter({
      ...me,
      has_voted: status.has_voted ?? me.has_voted,
      face_enrolled: status.face_enrolled ?? me.face_enrolled,
      is_locked: status.is_locked ?? me.is_locked,
    })
    setDpt((prev) => {
      const map = new Map(prev.map((item) => [item.nim, item]))
      map.set(voter.nim, voter)
      return Array.from(map.values())
    })
    if (active?.positions) setJabatan(positionsFromSession(active))
    if (status?.can_vote === false) {
      setVerificationToken(null)
    }
    return { me, status, active }
  }

  const refreshAdminSnapshot = async (token = adminToken) => {
    if (!token) return null
    const [dashboard, voters, positions, results] = await Promise.all([
      api.admin.dashboard(token),
      api.admin.voters(token),
      api.admin.positions(token),
      api.admin.results(token).catch(() => null),
    ])
    syncVoterList(voters)
    syncPositions(positions)
    if (results) syncResults(results)
    return { dashboard, voters, positions, results }
  }

  const bootstrap = async () => {
    setLoading(true)
    try {
      const active = await api.election.active().catch(() => null)
      if (active?.positions) {
        setSession(active)
        setJabatan(positionsFromSession(active))
      }

      const student = getStudentToken()
      if (student) {
        setStudentTokenState(student)
        await refreshStudentSnapshot(student)
      }

      const admin = getAdminToken()
      if (admin) {
        setAdminTokenState(admin)
        await refreshAdminSnapshot(admin)
      }
    } catch {
      setDpt(cloneJson(MOCK_DPT))
      setJabatan(cloneJson(JABATAN))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void bootstrap()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const findVoter = (nim) => dpt.find((v) => v.nim === nim)

  const setStudentSession = (token, user) => {
    setStudentTokenState(token)
    setStudentToken(token)
    setCurrentUser(user)
    setCurrentNim(user?.nim ?? null)
  }

  const setAdminSession = (token) => {
    setAdminTokenState(token)
    setAdminToken(token)
  }

  const loginStudent = async ({ nim, password }) => {
    const response = await api.auth.login({ nim, password })
    setStudentSession(response.access_token, response.user)
    await refreshStudentSnapshot(response.access_token)
    return response
  }

  const registerStudent = async ({ nim, nama, email, password, kelas }) => {
    const response = await api.auth.register({ nim, nama, email, password, kelas })
    setStudentSession(response.access_token, response.user)
    await refreshStudentSnapshot(response.access_token)
    return response
  }

  const requestPasswordReset = async (nim) => api.auth.requestReset({ nim })
  const confirmPasswordReset = async ({ nim, code, new_password }) =>
    api.auth.confirmReset({ nim, code, new_password })

  // frames: [{ pose, imageBase64 }]
  const enrollFace = async ({ nim, frames }) => {
    const response = await api.face.enroll(
      { nim, frames: frames.map((f) => ({ pose: f.pose, image_base64: f.imageBase64 })) },
      studentToken,
    )
    await refreshStudentSnapshot(studentToken)
    return response
  }

  const verifyFace = async ({
    nim,
    imageBase64,
    stage = 'match',
    challenge = null,
    timedOut = false,
    kioskDeviceId = null,
  }) => {
    const response = await api.face.verify(
      {
        nim,
        image_base64: imageBase64,
        stage,
        challenge,
        timed_out: timedOut,
        kiosk_device_id: kioskDeviceId,
      },
      studentToken,
    )
    if (response.verification_token) {
      setVerificationToken(response.verification_token)
    }
    // Hindari refresh snapshot pada tiap frame streaming; cukup saat final.
    if (response.verified || response.lock_applied) {
      await refreshStudentSnapshot(studentToken)
    }
    return response
  }

  const loginAdmin = async ({ username, password }) => {
    const response = await api.admin.login({ username, password })
    setAdminSession(response.access_token)
    await refreshAdminSnapshot(response.access_token)
    return response
  }

  const logoutStudent = () => {
    clearStudentToken()
    setStudentTokenState(null)
    setCurrentUser(null)
    setCurrentNim(null)
    setVerificationToken(null)
    setDpt(cloneJson(MOCK_DPT))
    setJabatan(cloneJson(JABATAN))
  }

  const logoutAdmin = () => {
    clearAdminToken()
    setAdminTokenState(null)
  }

  const submitVotes = async (nim, selections) => {
    const activeSession = session || (await api.election.active().catch(() => null))
    const positionLookup = new Map(jabatan.map((j) => [String(j.id), j]))
    const payload = Object.entries(selections).map(([positionId, candidateId]) => {
      const position = positionLookup.get(String(positionId))
      return {
        position_id: Number(position?.id ?? positionId),
        candidate_id: Number(candidateId),
      }
    })

    const response = await api.votes.submit(
      {
        session_id: Number(activeSession?.id ?? 1),
        nim,
        verification_token: verificationToken || '',
        selections: payload,
      },
      studentToken,
    )
    setVerificationToken(null)
    setLastVoteReference(response.vote_reference_code)
    await refreshStudentSnapshot(studentToken)
    if (adminToken) await refreshAdminSnapshot(adminToken)
    return response
  }

  // frames: [{ pose, imageBase64 }]
  const markFaceEnrolled = async (nim, frames) => {
    const response = await enrollFace({ nim, frames })
    return response
  }

  const markVoted = async (nim) => {
    const voter = findVoter(nim)
    if (voter) {
      setDpt((prev) => prev.map((item) => (item.nim === nim ? { ...item, hasVoted: true } : item)))
    }
  }

  const refreshElection = async () => {
    const active = await api.election.active()
    setSession(active)
    setJabatan(positionsFromSession(active))
    return active
  }

  const addVoter = async (voter) => {
    const response = await api.admin.createVoter(
      {
        nim: voter.nim,
        nama: voter.nama,
        kelas: voter.kelas ?? null,
        mode_akses: voter.modeAkses ?? voter.mode_akses ?? 'mandiri',
        email: voter.email ?? null,
        password: voter.password || null,
      },
      adminToken,
    )
    await refreshAdminSnapshot(adminToken)
    return response
  }

  // items: [{ nim, nama, kelas?, modeAkses?, email?, password? }]
  const bulkAddVoters = async (items) => {
    const response = await api.admin.bulkCreateVoters(
      {
        voters: items.map((v) => ({
          nim: v.nim,
          nama: v.nama,
          kelas: v.kelas ?? null,
          mode_akses: v.modeAkses ?? v.mode_akses ?? 'mandiri',
          email: v.email ?? null,
          password: v.password || null,
        })),
      },
      adminToken,
    )
    await refreshAdminSnapshot(adminToken)
    return response
  }

  const updateVoter = async (nim, patch) => {
    const response = await api.admin.updateVoter(
      nim,
      {
        nim,
        nama: patch.nama,
        kelas: patch.kelas ?? null,
        mode_akses: patch.modeAkses ?? patch.mode_akses ?? 'mandiri',
        email: patch.email ?? null,
        password: patch.password || null,
      },
      adminToken,
    )
    await refreshAdminSnapshot(adminToken)
    return response
  }

  const listAdminAccounts = async () => api.admin.accounts(adminToken)
  const addAdminAccount = async (account) => api.admin.createAccount(account, adminToken)
  const updateAdminAccount = async (id, patch) => api.admin.updateAccount(id, patch, adminToken)
  const deleteAdminAccount = async (id) => api.admin.deleteAccount(id, adminToken)

  const deleteVoter = async (nim) => {
    const response = await api.admin.deleteVoter(nim, adminToken)
    await refreshAdminSnapshot(adminToken)
    return response
  }

  const addJabatan = async (nama) => {
    const response = await api.admin.createPosition({ name: nama, is_required: true }, adminToken)
    await refreshAdminSnapshot(adminToken)
    return response
  }

  const updateJabatan = async (jabatanId, patch) => {
    const response = await api.admin.updatePosition(
      jabatanId,
      { name: patch.nama ?? patch.name, is_required: patch.is_required ?? true },
      adminToken,
    )
    await refreshAdminSnapshot(adminToken)
    return response
  }

  const deleteJabatan = async (jabatanId) => {
    const response = await api.admin.deletePosition(jabatanId, adminToken)
    await refreshAdminSnapshot(adminToken)
    return response
  }

  const addKandidat = async (jabatanId, kandidat) => {
    const response = await api.admin.createCandidate(
      jabatanId,
      {
        name: kandidat.nama ?? kandidat.name,
        number: Number(kandidat.nomor ?? kandidat.number),
        vision: kandidat.visi ?? kandidat.vision ?? '',
        photo_path: kandidat.photo_path ?? null,
        color: kandidat.warna ?? kandidat.color ?? '#2563eb',
      },
      adminToken,
    )
    await refreshAdminSnapshot(adminToken)
    return response
  }

  const updateKandidat = async (jabatanId, kandidatId, patch) => {
    const response = await api.admin.updateCandidate(
      jabatanId,
      kandidatId,
      {
        name: patch.nama ?? patch.name,
        number: Number(patch.nomor ?? patch.number),
        vision: patch.visi ?? patch.vision ?? '',
        photo_path: patch.photo_path ?? null,
        color: patch.warna ?? patch.color ?? '#2563eb',
      },
      adminToken,
    )
    await refreshAdminSnapshot(adminToken)
    return response
  }

  const deleteKandidat = async (jabatanId, kandidatId) => {
    const response = await api.admin.deleteCandidate(jabatanId, kandidatId, adminToken)
    await refreshAdminSnapshot(adminToken)
    return response
  }

  const loadAdminResults = async () => {
    const results = await api.admin.results(adminToken)
    syncResults(results)
    return results
  }

  const value = {
    loading,
    isOnlineMode,
    dpt,
    jabatan,
    votes,
    session,
    currentNim,
    currentUser,
    studentToken,
    adminToken,
    verificationToken,
    lastVoteReference,
    setCurrentNim,
    setVerificationToken,
    findVoter,
    loginStudent,
    registerStudent,
    requestPasswordReset,
    confirmPasswordReset,
    enrollFace,
    verifyFace,
    loginAdmin,
    logoutStudent,
    logoutAdmin,
    submitVotes,
    markFaceEnrolled,
    markVoted,
    addVoter,
    bulkAddVoters,
    updateVoter,
    deleteVoter,
    listAdminAccounts,
    addAdminAccount,
    updateAdminAccount,
    deleteAdminAccount,
    addJabatan,
    updateJabatan,
    deleteJabatan,
    addKandidat,
    updateKandidat,
    deleteKandidat,
    refreshElection,
    refreshStudentSnapshot,
    refreshAdminSnapshot,
    loadAdminResults,
  }

  return <MockStateContext.Provider value={value}>{children}</MockStateContext.Provider>
}

export function useMockState() {
  const ctx = useContext(MockStateContext)
  if (!ctx) throw new Error('useMockState must be used within MockStateProvider')
  return ctx
}
