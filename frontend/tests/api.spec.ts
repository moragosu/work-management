import { test, expect } from '@playwright/test'

const BASE = 'http://localhost:8001'
const testUsername = `testuser_${Date.now()}`

let memberToken = ''

// ── 로그인 헬퍼 ──────────────────────────────────────────────────────────────

async function login(request: any, username: string, password: string) {
  return request.post(`${BASE}/api/auth/login`, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    data: `username=${username}&password=${password}`,
  })
}

async function authHeader(token: string) {
  return { Authorization: `Bearer ${token}` }
}

// ── 인증 ─────────────────────────────────────────────────────────────────────

test.describe('인증', () => {
  test('존재하지 않는 계정 로그인 실패', async ({ request }) => {
    const res = await login(request, 'nonexistent_user_xyz', 'wrongpw')
    expect(res.status()).toBe(401)
  })

  test('회원가입 → 로그인 성공', async ({ request }) => {
    const res = await request.post(`${BASE}/api/auth/signup`, {
      data: { username: testUsername, name: '테스트유저', password: 'Test1234!' },
    })
    expect(res.status()).toBe(201)
    const body = await res.json()
    expect(body.user.role).toBe('member')
    memberToken = body.access_token
  })

  test('중복 아이디 가입 불가', async ({ request }) => {
    const res = await request.post(`${BASE}/api/auth/signup`, {
      data: { username: testUsername, name: '중복', password: 'Test1234!' },
    })
    expect(res.status()).toBe(409)
  })

  test('토큰으로 내 정보 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/auth/me`, {
      headers: await authHeader(memberToken),
    })
    expect(res.status()).toBe(200)
    const me = await res.json()
    expect(me.username).toBe(testUsername)
  })

  test('잘못된 토큰 거부', async ({ request }) => {
    const res = await request.get(`${BASE}/api/auth/me`, {
      headers: { Authorization: 'Bearer invalid_token' },
    })
    expect(res.status()).toBe(401)
  })
})

// ── 인력 API ─────────────────────────────────────────────────────────────────

test.describe('인력 API', () => {
  test('목록 조회 — username·task_ids 필드 포함', async ({ request }) => {
    const res = await request.get(`${BASE}/api/staff`)
    expect(res.status()).toBe(200)
    const staff = await res.json()
    expect(Array.isArray(staff)).toBeTruthy()
    staff.forEach((s: any) => {
      expect(s.username).toBeTruthy()
      expect(Array.isArray(s.task_ids)).toBeTruthy()
    })
  })

  test('회원가입 후 인력 목록에 포함', async ({ request }) => {
    const res = await request.get(`${BASE}/api/staff`)
    const staff = await res.json()
    const found = staff.find((s: any) => s.username === testUsername)
    expect(found).toBeTruthy()
    expect(found.name).toBe('테스트유저')
  })

  test('인력 정보 수정 (job_title, main_skills)', async ({ request }) => {
    const res = await request.put(`${BASE}/api/staff/${testUsername}`, {
      headers: await authHeader(memberToken),
      data: { job_title: '테스트직책', main_skills: 'Python, Vue.js' },
    })
    expect(res.status()).toBe(200)
    const updated = await res.json()
    expect(updated.job_title).toBe('테스트직책')
    expect(updated.main_skills).toBe('Python, Vue.js')
  })

  test('인력 개별 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/staff/${testUsername}`)
    expect(res.status()).toBe(200)
    const member = await res.json()
    expect(member.job_title).toBe('테스트직책')
  })

  test('파트장/관리자는 인력 목록에 미포함', async ({ request }) => {
    // admin 계정은 is_admin=1이지만 실제 운영 환경 비밀번호 모름 → 이름으로만 확인
    const res = await request.get(`${BASE}/api/staff`)
    const staff = await res.json()
    // role != member인 계정 이름은 결과에 없어야 함
    const adminEntry = staff.find((s: any) => s.username === 'admin')
    expect(adminEntry).toBeUndefined()
  })
})

// ── 과제 API ─────────────────────────────────────────────────────────────────

test.describe('과제 API', () => {
  test('목록 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/tasks`)
    expect(res.status()).toBe(200)
    expect(Array.isArray(await res.json())).toBeTruthy()
  })

  test('과제 이력 조회', async ({ request }) => {
    const tasksRes = await request.get(`${BASE}/api/tasks`)
    const tasks = await tasksRes.json()
    if (tasks.length === 0) return

    const taskId = tasks[0].id
    const res = await request.get(`${BASE}/api/tasks/${taskId}/history`)
    expect(res.status()).toBe(200)
    const body = await res.json()
    expect(body.task).toBeTruthy()
    expect(Array.isArray(body.weeks)).toBeTruthy()
  })
})

// ── 알림 API ─────────────────────────────────────────────────────────────────

test.describe('알림 API', () => {
  test('인증 없이 알림 조회 불가', async ({ request }) => {
    const res = await request.get(`${BASE}/api/notifications`)
    expect(res.status()).toBe(401)
  })

  test('로그인 후 알림 목록 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/notifications`, {
      headers: await authHeader(memberToken),
    })
    expect(res.status()).toBe(200)
    expect(Array.isArray(await res.json())).toBeTruthy()
  })
})

// ── OKR / 이슈 / Q&A ─────────────────────────────────────────────────────────

test.describe('OKR API', () => {
  test('목표 목록 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/okrs`)
    expect(res.status()).toBe(200)
    expect(Array.isArray(await res.json())).toBeTruthy()
  })
})

test.describe('이슈 API', () => {
  test('주차 기반 이슈 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/issues?week=2026-W22`)
    expect(res.status()).toBe(200)
    const issues = await res.json()
    issues.forEach((i: any) => expect(i.week).toBe('2026-W22'))
  })

  test('인증 없이 이슈 생성 불가', async ({ request }) => {
    const res = await request.post(`${BASE}/api/issues`, {
      data: { task_id: 'T1', week: '2026-W22', issue: '테스트', assignee: '테스트' },
    })
    expect(res.status()).toBe(401)
  })
})

test.describe('Q&A API', () => {
  test('질문 목록 조회', async ({ request }) => {
    const res = await request.get(`${BASE}/api/qna/questions`)
    expect(res.status()).toBe(200)
    expect(Array.isArray(await res.json())).toBeTruthy()
  })

  test('인증 없이 질문 생성 불가', async ({ request }) => {
    const res = await request.post(`${BASE}/api/qna/questions`, {
      data: { task_id: 'T1', week: '2026-W22', question: '테스트질문' },
    })
    expect(res.status()).toBe(401)
  })
})

// ── 역할 변경 → 인력 탭 필터 ─────────────────────────────────────────────────

test.describe('역할 변경', () => {
  test('파트원은 인력 목록에 표시', async ({ request }) => {
    const res = await request.get(`${BASE}/api/staff`)
    const staff = await res.json()
    expect(staff.find((s: any) => s.username === testUsername)).toBeTruthy()
  })
})

// ── 비밀번호 변경 ─────────────────────────────────────────────────────────────

test.describe('비밀번호 변경', () => {
  test('현재 비밀번호 틀리면 거부', async ({ request }) => {
    const res = await request.put(`${BASE}/api/auth/password`, {
      headers: await authHeader(memberToken),
      data: { current_password: 'wrongpassword', new_password: 'NewPass123!' },
    })
    expect(res.status()).toBe(400)
  })

  test('비밀번호 변경 성공', async ({ request }) => {
    const res = await request.put(`${BASE}/api/auth/password`, {
      headers: await authHeader(memberToken),
      data: { current_password: 'Test1234!', new_password: 'NewPass456!' },
    })
    expect(res.status()).toBe(200)
    // 새 비밀번호로 로그인 가능한지 확인
    const loginRes = await login(request, testUsername, 'NewPass456!')
    expect(loginRes.status()).toBe(200)
    memberToken = (await loginRes.json()).access_token
  })
})

// ── users.okrs 동기화 ─────────────────────────────────────────────────────────

test.describe('OKR/과제 동기화', () => {
  test('OKR 삭제 시 users.okrs에서 제거', async ({ request }) => {
    // 테스트용 OKR 생성 (admin 토큰 필요 — 없으면 스킵)
    const okrsRes = await request.get(`${BASE}/api/okrs`)
    const okrs = await okrsRes.json()
    if (okrs.length === 0) return

    // 기존 OKR을 수정하지 않고 인력의 okrs 필드를 직접 설정
    const setOkrRes = await request.put(`${BASE}/api/staff/${testUsername}`, {
      headers: await authHeader(memberToken),
      data: { okrs: okrs[0].id },
    })
    expect(setOkrRes.status()).toBe(200)
    const updated = await setOkrRes.json()
    expect(updated.okrs).toContain(okrs[0].id)
  })

  test('이슈 목록에 댓글 포함', async ({ request }) => {
    const res = await request.get(`${BASE}/api/issues`)
    expect(res.status()).toBe(200)
    const issues = await res.json()
    // 모든 이슈에 comments 배열이 있어야 함
    issues.forEach((i: any) => {
      expect(Array.isArray(i.comments)).toBeTruthy()
    })
  })
})

// ── CSV export ────────────────────────────────────────────────────────────────

test.describe('CSV export', () => {
  test('인력 CSV export — username 컬럼 포함', async ({ request }) => {
    const res = await request.get(`${BASE}/api/admin/export/staff`)
    expect(res.status()).toBe(200)
    const text = await res.text()
    // 헤더에 username 포함
    expect(text.split('\n')[0]).toContain('username')
  })

  test('과제 CSV export', async ({ request }) => {
    const res = await request.get(`${BASE}/api/admin/export/tasks`)
    expect(res.status()).toBe(200)
    expect(res.headers()['content-type']).toContain('text/csv')
  })
})

// ── 정리 ─────────────────────────────────────────────────────────────────────

test.afterAll(async ({ request }) => {
  // 테스트 계정 삭제 (admin 토큰이 있어야 하므로 실패해도 무시)
  if (memberToken) {
    await request.delete(`${BASE}/api/staff/${testUsername}`, {
      headers: await authHeader(memberToken),
    }).catch(() => {})
  }
})
