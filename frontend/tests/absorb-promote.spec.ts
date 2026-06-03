import { test, expect } from '@playwright/test'

const BASE = 'http://localhost:8001'

async function login(request: any) {
  const res = await request.post(`${BASE}/api/auth/login`, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    data: 'username=admin&password=admin123',
  })
  const body = await res.json()
  return body.access_token as string
}

function auth(token: string) {
  return { Authorization: `Bearer ${token}` }
}

// ── 헬퍼 ─────────────────────────────────────────────────────────────────────

async function getTasks(request: any, token: string) {
  const res = await request.get(`${BASE}/api/tasks`, { headers: auth(token) })
  return (await res.json()) as any[]
}

async function getTask(request: any, token: string, id: string) {
  const res = await request.get(`${BASE}/api/tasks/${id}`, { headers: auth(token) })
  return res.status() === 200 ? await res.json() : null
}

async function createTask(request: any, token: string, id: string, name: string, objectiveId = '') {
  const res = await request.post(`${BASE}/api/tasks`, {
    headers: { ...auth(token), 'Content-Type': 'application/json' },
    data: JSON.stringify({ id, name, objective_id: objectiveId, target: '', members: [], sub_tasks: [] }),
  })
  return res.status()
}

async function createIssue(request: any, token: string, taskId: string, week: string) {
  const res = await request.post(`${BASE}/api/issues`, {
    headers: { ...auth(token), 'Content-Type': 'application/json' },
    data: JSON.stringify({ task_id: taskId, week, issue: '<p>테스트 이슈</p>', assignee: '테스트' }),
  })
  return res.status() === 201 ? (await res.json()).id : null
}

async function absorb(request: any, token: string, taskId: string, parentId: string, newSubId: string) {
  return request.post(`${BASE}/api/tasks/${taskId}/absorb`, {
    headers: { ...auth(token), 'Content-Type': 'application/json' },
    data: JSON.stringify({ parent_id: parentId, new_sub_id: newSubId }),
  })
}

async function promote(request: any, token: string, subId: string, parentId: string, newTaskId: string) {
  return request.post(`${BASE}/api/tasks/${subId}/promote`, {
    headers: { ...auth(token), 'Content-Type': 'application/json' },
    data: JSON.stringify({ parent_id: parentId, new_task_id: newTaskId }),
  })
}

async function deleteTask(request: any, token: string, id: string) {
  await request.delete(`${BASE}/api/tasks/${id}`, { headers: auth(token) })
}

// ── 테스트 데이터 ─────────────────────────────────────────────────────────────

const TA = 'TA_TEST'
const TB = 'TB_TEST'
const TC = 'TC_TEST'
let token = ''

test.describe('편입·분리 기능', () => {

  test.beforeAll(async ({ request }) => {
    token = await login(request)
    // 테스트 과제 생성
    await createTask(request, token, TA, '테스트 과제A')
    await createTask(request, token, TB, '테스트 과제B')
    await createTask(request, token, TC, '테스트 과제C')
  })

  test.afterAll(async ({ request }) => {
    // 정리: 테스트 과제 삭제 (분리 결과로 생긴 것 포함)
    const tasks = await getTasks(request, token)
    const testIds = tasks
      .filter(t => t.name?.includes('테스트 과제') || t.id.startsWith('TA_') || t.id.startsWith('TB_') || t.id.startsWith('TC_'))
      .map(t => t.id)
    for (const id of testIds) {
      await request.delete(`${BASE}/api/tasks/${id}`, { headers: auth(token) })
    }
  })

  // ── 재사용 가능 소과제 ID 조회 ──────────────────────────────────────────────

  test('reusable-sub-ids: 빈 모과제 → next만 반환', async ({ request }) => {
    const res = await request.get(`${BASE}/api/tasks/${TB}/reusable-sub-ids`, { headers: auth(token) })
    expect(res.status()).toBe(200)
    const body = await res.json()
    expect(body.next).toBe(`${TB}-1`)
    expect(body.reusable).toEqual([])
  })

  // ── 편입 정상 동작 ────────────────────────────────────────────────────────

  test('TA를 TB의 소과제로 편입 → TB-1 부여', async ({ request }) => {
    const res = await absorb(request, token, TA, TB, `${TB}-1`)
    expect(res.status()).toBe(200)
    const body = await res.json()
    const sub = body.sub_tasks.find((s: any) => s.id === `${TB}-1`)
    expect(sub).toBeTruthy()
    expect(sub.name).toBe('테스트 과제A')
  })

  test('편입 후 TA가 대과제 목록에서 사라짐', async ({ request }) => {
    const tasks = await getTasks(request, token)
    expect(tasks.find(t => t.id === TA)).toBeUndefined()
  })

  test('reusable-sub-ids: TB-1 편입 후 다음 순번은 TB-2', async ({ request }) => {
    const res = await request.get(`${BASE}/api/tasks/${TB}/reusable-sub-ids`, { headers: auth(token) })
    const body = await res.json()
    expect(body.next).toBe(`${TB}-2`)
    expect(body.reusable).toEqual([])
  })

  // ── 편입 방어 로직 ────────────────────────────────────────────────────────

  test('자기 자신에게 편입 → 400', async ({ request }) => {
    const res = await absorb(request, token, TC, TC, `${TC}-1`)
    expect(res.status()).toBe(400)
  })

  test('잘못된 소과제 ID 형식 → 400', async ({ request }) => {
    const res = await absorb(request, token, TC, TB, 'wrongformat')
    expect(res.status()).toBe(400)
  })

  test('잘못된 소과제 ID 형식2 (부모 ID 불일치) → 400', async ({ request }) => {
    const res = await absorb(request, token, TC, TB, `${TC}-1`)
    expect(res.status()).toBe(400)
  })

  test('이미 사용 중인 소과제 ID → 400', async ({ request }) => {
    // TB-1은 TA가 편입되어 있음
    const res = await absorb(request, token, TC, TB, `${TB}-1`)
    expect(res.status()).toBe(400)
  })

  // ── 소과제 순 정렬 ─────────────────────────────────────────────────────────

  test('TC를 TB-2로 편입 → TB-1, TB-2 순 정렬', async ({ request }) => {
    const res = await absorb(request, token, TC, TB, `${TB}-2`)
    expect(res.status()).toBe(200)
    const body = await res.json()
    const ids = body.sub_tasks.map((s: any) => s.id)
    expect(ids).toEqual([`${TB}-1`, `${TB}-2`])
  })

  // ── DB 참조 이전 ──────────────────────────────────────────────────────────

  test('편입 전 이슈 생성 → 편입 후 새 ID로 조회 가능', async ({ request }) => {
    // 새 과제 생성, 이슈 추가, 편입 → 이슈 task_id 업데이트 확인
    const newId = 'TD_TEST'
    await createTask(request, token, newId, '테스트 과제D')

    const issueId = await createIssue(request, token, newId, '2026-W22')
    expect(issueId).toBeTruthy()

    // TB에 편입 (TB-1, TB-2 이미 있으므로 TB-3)
    const res = await absorb(request, token, newId, TB, `${TB}-3`)
    expect(res.status()).toBe(200)

    // 이슈가 새 ID(TB-3)로 조회되는지 확인
    const issuesRes = await request.get(`${BASE}/api/issues?task_id=${TB}-3`, { headers: auth(token) })
    const issues = await issuesRes.json()
    const found = issues.find((i: any) => i.id === issueId)
    expect(found).toBeTruthy()
    expect(found.task_id).toBe(`${TB}-3`)

    // 구 ID로는 조회 안 됨
    const oldIssues = await request.get(`${BASE}/api/issues?task_id=${newId}`, { headers: auth(token) })
    const oldList = await oldIssues.json()
    expect(oldList.find((i: any) => i.id === issueId)).toBeUndefined()
  })

  // ── 소과제 target 저장 ────────────────────────────────────────────────────

  test('소과제 target 업데이트', async ({ request }) => {
    const res = await request.put(`${BASE}/api/tasks/${TB}/sub-tasks/${TB}-1`, {
      headers: { ...auth(token), 'Content-Type': 'application/json' },
      data: JSON.stringify({ target: 'MX' }),
    })
    expect(res.status()).toBe(200)
    const sub = await res.json()
    expect(sub.target).toBe('MX')
  })

  // ── 분리 정상 동작 ────────────────────────────────────────────────────────

  test('TB-2 소과제 → 독립 과제로 분리', async ({ request }) => {
    const res = await promote(request, token, `${TB}-2`, TB, 'T8901')
    expect(res.status()).toBe(200)
    const body = await res.json()
    expect(body.id).toBe('T8901')
    expect(body.objective_id).toBe('')  // objective 해제
  })

  test('분리 후 TB 소과제에서 TB-2 사라짐', async ({ request }) => {
    const tb = await getTask(request, token, TB)
    expect(tb.sub_tasks.find((s: any) => s.id === `${TB}-2`)).toBeUndefined()
  })

  test('분리된 T8901이 대과제로 존재', async ({ request }) => {
    const te = await getTask(request, token, 'T8901')
    expect(te).toBeTruthy()
    expect(te.name).toBe('테스트 과제C')
    // 정리
    await deleteTask(request, token, 'T8901')
  })

  // ── 분리 방어 로직 ────────────────────────────────────────────────────────

  test('잘못된 분리 ID 형식 → 400', async ({ request }) => {
    const res = await promote(request, token, `${TB}-1`, TB, 'TXabc')  // 숫자 아님
    expect(res.status()).toBe(400)
  })

  test('이미 존재하는 ID로 분리 → 400', async ({ request }) => {
    const res = await promote(request, token, `${TB}-1`, TB, 'T1')  // 기존 과제
    expect(res.status()).toBe(400)
  })

  // ── 소과제 보유 과제 편입 불가 ────────────────────────────────────────────

  test('소과제 있는 과제 편입 시도 → 400', async ({ request }) => {
    // TB는 현재 TB-1, TB-3 소과제 보유
    const newId = 'TF_TEST'
    await createTask(request, token, newId, '테스트 과제F')
    const res = await absorb(request, token, TB, newId, `${newId}-1`)
    expect(res.status()).toBe(400)
    await deleteTask(request, token, newId)
  })
})
