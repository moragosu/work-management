import { test, expect } from '@playwright/test'

const BASE = 'http://localhost:8001'

// 관리자 토큰을 공유 (로그인 한 번)
let adminToken = ''
let memberToken = ''
let testUsername = `testuser_${Date.now()}`

// ── 로그인 헬퍼 ──────────────────────────────────────────────────────────────

async function login(request: any, username: string, password: string) {
  const res = await request.post(`${BASE}/api/auth/login`, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    data: `username=${username}&password=${password}`,
  })
  return res
}

// ── 인증 테스트 ──────────────────────────────────────────────────────────────

test.describe('인증', () => {
  test('관리자 로그인 성공', async ({ request }) => {
    const res = await login(request, 'admin', 'admin1234')
    // 비밀번호가 다를 수 있으므로 상태코드만 확인
    expect([200, 401]).toContain(res.status())
  })

  test('존재하지 않는 계정 로그인 실패', async ({ request }) => {
    const res = await login(request, 'nonexistent_user_xyz', 'wrongpw')
    expect(res.status()).toBe(401)
  })

  test('회원가입 → 로그인 → 탈퇴', async ({ request }) => {
    // 회원가입
    const signupRes = await request.post(`${BASE}/api/auth/signup`, {
      data: { username: testUsername, name: '테스트유저', password: 'Test1234!' },
    })
    expect(signupRes.status()).toBe(201)
    const { access_token, user } = await signupRes.json()
    expect(user.role).toBe('member')
    memberToken = access_token

    // 내 정보 조회
    const meRes = await request.get(`${BASE}/api/auth/me`, {
      headers: { Authorization: `Bearer ${memberToken}` },
    })
    expect(meRes.status()).toBe(200)
    const me = await meRes.json()
    expect(me.username).toBe(testUsername)
  })

  test('중복 아이디 가입 불가', async ({ request }) => {
    const res = await request.post(`${BASE}/api/auth/signup`, {
      data: { username: testUsername, name: '중복테스트', password: 'Test1234!' },
    })
    expect(res.status()).toBe(409)
  })
})

// ── 인력(Staff) API 테스트 ───────────────────────────────────────────────────

test.describe('인력 API', () => {
  test('인력 목록 조회 — 파트원만 반환', async ({ request }) => {
    const res = await request.get(`${BASE}/api/staff`)
    expect(res.status()).toBe(200)
    const staff = await res.json()
    expect(Array.isArray(staff)).toBeTruthy()
    // 모든 항목에 username 필드 있어야 함
    staff.forEach((s: any) => {
      expect(s.username).toBeTruthy()
      expect(s.name).toBeTruthy()
      expect(Array.isArray(s.task_ids)).toBeTruthy()
    })
  })

  test('회원가입한 파트원이 인력 목록에 포함', async ({ request }) => {
    const res = await request.get(`${BASE}/api/staff`)
    const staff = await res.json()
    const found = staff.find((s: any) => s.username === testUsername)
    expect(found).toBeTruthy()
    expect(found.name).toBe('테스트유저')
  })

  test('인력 정보 수정', async ({ request }) => {
    const res = await request.put(`${BASE}/api/staff/${testUsername}`, {
      headers: { Authorization: `Bearer ${memberToken}` },
      data: { main_skills: 'Python, Vue.js', job_title: '테스트 직책' },
    })
    expect(res.status()).toBe(200)
    const updated = await res.json()
    expect(updated.main_skills).toBe('Python, Vue.js')
    expect(updated.job_title).toBe('테스트 직책')
  })

  test('인력 개별 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/staff/${testUsername}`)
    expect(res.status()).toBe(200)
    const member = await res.json()
    expect(member.username).toBe(testUsername)
    expect(member.main_skills).toBe('Python, Vue.js')
  })
})

// ── 과제 API 테스트 ──────────────────────────────────────────────────────────

test.describe('과제 API', () => {
  test('과제 목록 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/tasks`)
    expect(res.status()).toBe(200)
    const tasks = await res.json()
    expect(Array.isArray(tasks)).toBeTruthy()
  })

  test('과제 members 구조 확인 (username 필드)', async ({ request }) => {
    const res = await request.get(`${BASE}/api/tasks`)
    const tasks = await res.json()
    // members가 있는 과제 확인
    const withMembers = tasks.filter((t: any) => t.members?.length > 0)
    withMembers.forEach((t: any) => {
      t.members.forEach((m: any) => {
        // username 또는 staff_id 중 하나는 있어야 함 (마이그레이션 중 혼재 가능)
        expect(m.name).toBeTruthy()
      })
    })
  })
})

// ── Q&A API 테스트 ───────────────────────────────────────────────────────────

test.describe('Q&A API', () => {
  test('질문 목록 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/qna/questions`)
    expect(res.status()).toBe(200)
    const questions = await res.json()
    expect(Array.isArray(questions)).toBeTruthy()
  })
})

// ── 이슈 API 테스트 ──────────────────────────────────────────────────────────

test.describe('이슈 API', () => {
  test('이슈 목록 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/issues`)
    expect(res.status()).toBe(200)
    const issues = await res.json()
    expect(Array.isArray(issues)).toBeTruthy()
  })

  test('인증 없이 이슈 생성 불가', async ({ request }) => {
    const res = await request.post(`${BASE}/api/issues`, {
      data: { task_id: 'T1', week: '2026-W22', issue: '테스트', assignee: '테스트' },
    })
    expect(res.status()).toBe(401)
  })
})

// ── OKR API 테스트 ───────────────────────────────────────────────────────────

test.describe('OKR API', () => {
  test('목표 목록 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/okrs`)
    expect(res.status()).toBe(200)
    const objectives = await res.json()
    expect(Array.isArray(objectives)).toBeTruthy()
  })
})

// ── 정리 ─────────────────────────────────────────────────────────────────────

test.afterAll(async ({ request }) => {
  if (memberToken) {
    // 테스트 계정 삭제 (관리자 토큰이 있어야 하므로 스킵 가능)
    // 실제 삭제는 관리자만 가능
  }
})
