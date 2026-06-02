import { test, expect, Page } from '@playwright/test'

const UI_BASE = 'http://localhost:5174'
const ADMIN = { username: 'admin', password: 'admin123' }

async function login(page: Page, username = ADMIN.username, password = ADMIN.password) {
  await page.goto(`${UI_BASE}/login`)
  await page.fill('input[type="text"]', username)
  await page.fill('input[type="password"]', password)
  await page.click('button[type="submit"]')
  await page.waitForURL(`${UI_BASE}/dashboard`, { timeout: 5000 })
}

// ── 인증 ─────────────────────────────────────────────────────────────────────

test.describe('로그인 / 인증', () => {
  test('로그인 페이지 렌더링', async ({ page }) => {
    await page.goto(`${UI_BASE}/login`)
    await expect(page.locator('h2')).toHaveText('로그인')
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('잘못된 비밀번호 → 오류 메시지', async ({ page }) => {
    await page.goto(`${UI_BASE}/login`)
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')
    await expect(page.locator('.auth-error')).toBeVisible({ timeout: 3000 })
  })

  test('admin 로그인 성공 → 대시보드 이동', async ({ page }) => {
    await login(page)
    await expect(page).toHaveURL(`${UI_BASE}/dashboard`)
    await expect(page.locator('.sidebar')).toBeVisible()
  })

  test('미로그인 상태에서 대시보드 접근 → 로그인 리다이렉트', async ({ page }) => {
    await page.goto(`${UI_BASE}/dashboard`)
    await expect(page).toHaveURL(/\/login/)
  })

  test('로그아웃 → 로그인 페이지 이동', async ({ page }) => {
    await login(page)
    await page.click('.logout-btn')
    await expect(page).toHaveURL(`${UI_BASE}/login`)
  })
})

// ── 대시보드 ─────────────────────────────────────────────────────────────────

test.describe('대시보드', () => {
  test.beforeEach(async ({ page }) => { await login(page) })

  test('KPI 카드 3개 표시', async ({ page }) => {
    const cards = page.locator('.stat-card')
    await expect(cards).toHaveCount(3, { timeout: 5000 })
  })

  test('사이드바 네비게이션 메뉴 표시', async ({ page }) => {
    const navItems = page.locator('.nav-item')
    await expect(navItems).toHaveCount(5)
    await expect(navItems.nth(0)).toContainText('대시보드')
    await expect(navItems.nth(1)).toContainText('주간 진행 현황')
  })

  test('상단 바 유저 이름 표시', async ({ page }) => {
    await expect(page.locator('.user-name')).toBeVisible()
  })

  test('알림 벨 아이콘 표시', async ({ page }) => {
    await expect(page.locator('.bell-btn')).toBeVisible()
  })

  test('목표 현황 섹션 표시', async ({ page }) => {
    const objSection = page.locator('.obj-card').first()
    await expect(objSection).toBeVisible({ timeout: 5000 })
  })

  test('파트 공지 섹션 — admin 모드 활성화 시 표시', async ({ page }) => {
    // adminMode는 localStorage 기반 토글. 새 세션에서 활성화 후 확인
    await page.addInitScript(() => localStorage.setItem('adminMode', 'true'))
    await login(page)
    await expect(page.locator('.notice-card')).toBeVisible({ timeout: 5000 })
  })
})

// ── 주간 진행 현황 ───────────────────────────────────────────────────────────

test.describe('주간 진행 현황', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.click('text=주간 진행 현황')
    await page.waitForURL(`${UI_BASE}/progress`, { timeout: 5000 })
  })

  test('진행 현황 페이지 렌더링', async ({ page }) => {
    await expect(page.locator('.page-header h2')).toContainText('주간 진행 현황')
  })

  test('이번주 / 지난주 패널 전환 버튼', async ({ page }) => {
    const toggleBtns = page.locator('.panel-toggle-btn, .panel-btn, [class*="toggle"]').filter({ hasText: /이번주|지난주/ })
    await expect(toggleBtns.first()).toBeVisible({ timeout: 3000 })
  })

  test('과제 카드 1개 이상 표시', async ({ page }) => {
    // Progress.vue 과제 카드는 .card.mb-16 클래스 사용
    await expect(page.locator('.page-body .card.mb-16').first()).toBeVisible({ timeout: 5000 })
  })
})

// ── 관리 도구 ────────────────────────────────────────────────────────────────

test.describe('관리 도구', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.click('text=관리 도구')
    await page.waitForURL(`${UI_BASE}/admin`, { timeout: 5000 })
  })

  test('관리 도구 페이지 렌더링', async ({ page }) => {
    await expect(page.locator('.page-header h2')).toContainText('관리 도구')
  })

  test('탭 메뉴 표시 (목표/과제/인력/계정)', async ({ page }) => {
    const tabs = page.locator('.tab')
    await expect(tabs.first()).toBeVisible()
    const count = await tabs.count()
    expect(count).toBeGreaterThanOrEqual(3)
  })

  test('목표 탭 — 목표 목록 표시', async ({ page }) => {
    await page.click('.tab >> text=목표')
    await expect(page.locator('table tbody tr').first()).toBeVisible({ timeout: 3000 })
  })
})

// ── 알림 ─────────────────────────────────────────────────────────────────────

test.describe('알림', () => {
  test.beforeEach(async ({ page }) => { await login(page) })

  test('알림 벨 클릭 → 드롭다운 열림', async ({ page }) => {
    await page.click('.bell-btn')
    await expect(page.locator('.bell-dropdown')).toBeVisible({ timeout: 3000 })
  })

  test('알림 드롭다운 헤더 "알림" 텍스트', async ({ page }) => {
    await page.click('.bell-btn')
    await expect(page.locator('.bell-title')).toContainText('알림')
  })

  test('알림 드롭다운 외부 클릭 → 닫힘', async ({ page }) => {
    await page.click('.bell-btn')
    await expect(page.locator('.bell-dropdown')).toBeVisible()
    await page.click('.page-title')
    await expect(page.locator('.bell-dropdown')).not.toBeVisible({ timeout: 2000 })
  })
})

// ── 네비게이션 ───────────────────────────────────────────────────────────────

test.describe('네비게이션', () => {
  test.beforeEach(async ({ page }) => { await login(page) })

  test('피드백 메뉴 이동', async ({ page }) => {
    await page.click('text=피드백')
    await expect(page).toHaveURL(`${UI_BASE}/feedback`)
  })

  test('도움말 메뉴 이동', async ({ page }) => {
    await page.click('text=도움말')
    await expect(page).toHaveURL(`${UI_BASE}/help`)
  })

  test('로고 클릭 → 대시보드 이동', async ({ page }) => {
    await page.goto(`${UI_BASE}/help`)
    await page.click('.sidebar-logo')
    await expect(page).toHaveURL(`${UI_BASE}/dashboard`)
  })
})
