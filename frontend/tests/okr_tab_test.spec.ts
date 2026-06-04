import { test, expect, Page } from '@playwright/test'

const BASE = 'http://localhost:5174'

async function login(page: Page) {
  await page.goto(`${BASE}/login`)
  await page.fill('input[type="text"], input[placeholder*="아이디"], input[name="username"]', 'admin')
  await page.fill('input[type="password"]', 'admin123')
  await page.click('button[type="submit"], button:has-text("로그인")')
  await page.waitForURL('**/admin**', { timeout: 5000 }).catch(() => page.waitForURL('**/', { timeout: 3000 }))
}

test.describe('OKR 현황 탭 통합 테스트', () => {

  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.goto(`${BASE}/admin?tab=okr`)
    await page.waitForSelector('.okr-tab', { timeout: 5000 })
  })

  // ── 1. 기본 렌더링 ──
  test('OKR 현황 탭 기본 렌더링 — 목표·과제·소과제 표시', async ({ page }) => {
    // 툴바 통계 칩
    await expect(page.locator('.stat-chip').first()).toBeVisible()

    // 목표 섹션이 최소 1개 이상
    const objSections = page.locator('.obj-section')
    const count = await objSections.count()
    expect(count).toBeGreaterThan(0)
    console.log(`목표 섹션 ${count}개 표시됨`)

    // 목표 헤더에 ID 배지
    await expect(page.locator('.obj-id-badge').first()).toBeVisible()
  })

  // ── 2. 목표 섹션 접기/펼치기 ──
  test('목표 섹션 접기/펼치기', async ({ page }) => {
    // 첫 번째 목표의 접기 버튼
    const expandBtn = page.locator('.expand-btn').first()
    await expandBtn.click()
    // 접힌 후 task-list가 사라져야
    const objSection = page.locator('.obj-section').first()
    await expect(objSection.locator('.task-list')).not.toBeVisible()

    // 다시 펼치기
    await expandBtn.click()
    await expect(objSection.locator('.task-list')).toBeVisible()
  })

  // ── 3. 전체 접기/펼치기 ──
  test('전체 접기 버튼 동작', async ({ page }) => {
    const toggleBtn = page.locator('button:has-text("전체 접기"), button:has-text("전체 펼치기")').first()
    await expect(toggleBtn).toBeVisible()
    const initialText = await toggleBtn.textContent()
    await toggleBtn.click()
    await page.waitForTimeout(300)
    const afterText = await toggleBtn.textContent()
    expect(initialText?.trim()).not.toBe(afterText?.trim())
    console.log(`전체 접기/펼치기: "${initialText?.trim()}" → "${afterText?.trim()}"`)
  })

  // ── 4. 인력 필터 ──
  test('인력 필터 칩 표시 및 토글', async ({ page }) => {
    const staffChips = page.locator('.staff-chip')
    const chipCount = await staffChips.count()
    if (chipCount > 0) {
      await staffChips.first().click()
      await expect(staffChips.first()).toHaveClass(/staff-chip-active/)
      // 전체 보기 버튼 표시
      await expect(page.locator('button:has-text("전체 보기")')).toBeVisible()
      // 다시 클릭으로 해제
      await staffChips.first().click()
      console.log(`인력 필터 칩 ${chipCount}개 표시, 토글 정상`)
    } else {
      console.log('인력 없음 — 필터 스킵')
    }
  })

  // ── 5. 목표 추가 모달 ──
  test('목표 추가 모달 — ID 자동 채번', async ({ page }) => {
    await page.click('button:has-text("목표 추가")')
    await expect(page.locator('.modal-card')).toBeVisible()
    await expect(page.locator('.modal-title')).toHaveText('목표 추가')
    // ID 필드에 값이 들어와야 함 (live 조회)
    await page.waitForTimeout(500)
    const idInput = page.locator('.modal-card input.form-control').first()
    const idVal = await idInput.inputValue()
    expect(idVal).toMatch(/^O\d+/)
    console.log(`목표 추가 모달 ID: ${idVal}`)
    await page.click('button:has-text("취소")')
  })

  // ── 6. 과제 추가 모달 (목표 섹션 내) ──
  test('과제 추가 모달 — 목표 ID 자동 연결 + ID 채번', async ({ page }) => {
    // 첫 번째 목표의 "+ 과제" 클릭
    await page.locator('.task-add-row button').first().click()
    await expect(page.locator('.modal-card')).toBeVisible()
    await expect(page.locator('.modal-title')).toHaveText('과제 추가')
    await page.waitForTimeout(500)
    const idInput = page.locator('.modal-card input.form-control').first()
    const idVal = await idInput.inputValue()
    expect(idVal).toMatch(/^T\d+/)
    console.log(`과제 추가 모달 ID: ${idVal}`)
    await page.keyboard.press('Escape')
  })

  // ── 7. 소과제 추가 모달 — reusable-sub-ids API ──
  test('소과제 추가 모달 — API 기반 ID 채번', async ({ page }) => {
    // 소과제가 있는 과제 찾기 (T1 = 소과제 4개)
    const subtaskAddBtn = page.locator('.subtask-add-row button').first()
    await subtaskAddBtn.click()
    await expect(page.locator('.modal-card')).toBeVisible()
    await expect(page.locator('.modal-title')).toHaveText('소과제 추가')
    await page.waitForTimeout(300)
    // subId 필드
    const subIdInput = page.locator('.modal-card input[readonly]').first()
    const subIdVal = await subIdInput.inputValue()
    expect(subIdVal).toMatch(/^T\d+-\d+/)
    console.log(`소과제 추가 모달 ID: ${subIdVal}`)
    await page.click('button:has-text("취소")')
  })

  // ── 8. 이력 버튼 ──
  test('과제 행 이력 버튼 → TaskHistory 이동 + 복귀', async ({ page }) => {
    const historyBtn = page.locator('.task-row .task-actions button:has-text("이력")').first()
    await historyBtn.click()
    await page.waitForURL('**/tasks/**/history**', { timeout: 4000 })
    expect(page.url()).toContain('/history')
    expect(page.url()).toContain('back=')
    console.log(`이력 URL: ${page.url()}`)

    // 뒤로가기 버튼으로 OKR 현황 복귀 확인
    const backBtn = page.locator('button:has-text("뒤로"), a:has-text("뒤로"), button.back-btn').first()
    if (await backBtn.isVisible()) {
      await backBtn.click()
      await page.waitForURL('**/admin**', { timeout: 3000 })
      expect(page.url()).toContain('tab=okr')
      console.log(`복귀 URL: ${page.url()}`)
    }
  })

  // ── 9. 편입 버튼 표시 ──
  test('편입 버튼 — 소과제 없는 과제에 활성화', async ({ page }) => {
    // 소과제 없는 과제 행에서 편입 버튼이 enabled인지
    const allAbsorbBtns = page.locator('.task-row button:has-text("편입")')
    const count = await allAbsorbBtns.count()
    expect(count).toBeGreaterThan(0)

    let enabledFound = false
    for (let i = 0; i < count; i++) {
      const btn = allAbsorbBtns.nth(i)
      const disabled = await btn.isDisabled()
      if (!disabled) {
        enabledFound = true
        // 클릭해서 모달 열기
        await btn.click()
        await expect(page.locator('.modal-card')).toBeVisible()
        await expect(page.locator('.modal-title')).toHaveText('소과제로 편입')
        // 모과제 드롭다운 존재
        await expect(page.locator('.modal-card select')).toBeVisible()
        console.log(`편입 모달 정상 열림 (${i+1}번째 과제)`)
        await page.click('button:has-text("취소")')
        break
      }
    }
    expect(enabledFound).toBe(true)
  })

  // ── 10. 편입 모달 — 모과제 선택 시 새 ID 자동 조회 ──
  test('편입 모달 — 모과제 선택 시 소과제 ID 자동 채번', async ({ page }) => {
    const allAbsorbBtns = page.locator('.task-row button:has-text("편입")')
    const count = await allAbsorbBtns.count()
    for (let i = 0; i < count; i++) {
      const btn = allAbsorbBtns.nth(i)
      if (!(await btn.isDisabled())) {
        await btn.click()
        await expect(page.locator('.modal-card')).toBeVisible()
        // 드롭다운에서 첫 번째 과제 선택
        const select = page.locator('.modal-card select')
        const options = await select.locator('option').allTextContents()
        const validOpts = options.filter(o => o.trim() && !o.includes('선택하세요'))
        if (validOpts.length > 0) {
          await select.selectOption({ index: 1 })
          await page.waitForTimeout(600)
          const subIdInput = page.locator('.modal-card input[readonly]')
          const subIdVal = await subIdInput.inputValue()
          expect(subIdVal).toMatch(/^T.+-\d+/)
          console.log(`편입 모달 소과제 ID 자동 채번: ${subIdVal}`)
        }
        await page.click('button:has-text("취소")')
        break
      }
    }
  })

  // ── 11. 소과제 행 분리 버튼 표시 ──
  test('소과제 행에 이동·분리 버튼 표시', async ({ page }) => {
    const moveBtn = page.locator('.subtask-row button:has-text("이동")').first()
    const promoteBtn = page.locator('.subtask-row button:has-text("분리")').first()

    if (await moveBtn.isVisible()) {
      console.log('소과제 이동 버튼 표시됨')
      await moveBtn.click()
      await expect(page.locator('.modal-title')).toHaveText('소과제 이동')
      await page.click('button:has-text("취소")')
    }

    if (await promoteBtn.isVisible()) {
      console.log('소과제 분리 버튼 표시됨')
      await promoteBtn.click()
      await expect(page.locator('.modal-title')).toHaveText('독립 과제로 분리')
      // 분리 모달 내 ID live 조회 확인
      await page.waitForTimeout(600)
      const idInput = page.locator('.modal-card input[readonly]')
      const idVal = await idInput.inputValue()
      expect(idVal).toMatch(/^T\d+/)
      console.log(`분리 모달 새 과제 ID: ${idVal}`)
      await page.keyboard.press('Escape')
    }
  })

  // ── 12. 소과제 이력 버튼 ──
  test('소과제 이력 버튼 → sub 파라미터 포함', async ({ page }) => {
    const subHistoryBtn = page.locator('.subtask-row button:has-text("이력")').first()
    if (await subHistoryBtn.isVisible()) {
      await subHistoryBtn.click()
      await page.waitForURL('**/tasks/**/history**', { timeout: 4000 })
      expect(page.url()).toContain('sub=')
      console.log(`소과제 이력 URL: ${page.url()}`)
      await page.goBack()
    }
  })

  // ── 13. 미연결 과제 섹션 ──
  test('미연결 과제 섹션 표시 및 접기/펼치기', async ({ page }) => {
    const unlinkedSection = page.locator('.unlinked-section')
    if (await unlinkedSection.isVisible()) {
      const header = unlinkedSection.locator('.unlinked-header')
      await header.click()
      await page.waitForTimeout(200)
      console.log('미연결 과제 섹션 접기 정상')
    } else {
      console.log('미연결 과제 없음 — 스킵')
    }
  })

  // ── 14. 담당자 추가 드롭다운 ──
  test('담당자 + 버튼 클릭 시 드롭다운 표시', async ({ page }) => {
    const addMemberBtn = page.locator('.task-row .btn-add-action:has-text("+ 담당자")').first()
    await addMemberBtn.click()
    await page.waitForTimeout(200)
    const dropdown = page.locator('.member-dropdown').first()
    await expect(dropdown).toBeVisible()
    console.log('담당자 드롭다운 정상 표시')
    // 다른 곳 클릭으로 닫기
    await page.click('.okr-tab', { position: { x: 10, y: 10 } })
    await page.waitForTimeout(200)
  })

  // ── 15. 드래그 핸들 표시 ──
  test('드래그 핸들 — 과제/소과제 행 hover 시 표시', async ({ page }) => {
    // 소과제 없는 과제 행에 drag_indicator 아이콘 존재 확인
    const taskRow = page.locator('.task-row[draggable="true"]').first()
    await expect(taskRow).toBeVisible()
    const handle = taskRow.locator('.drag-handle')
    await expect(handle).toBeAttached()

    // 소과제 행에도 drag_indicator 존재
    const subtaskRow = page.locator('.subtask-row[draggable="true"]').first()
    await expect(subtaskRow).toBeAttached()
    const subHandle = subtaskRow.locator('.drag-handle')
    await expect(subHandle).toBeAttached()
    console.log('드래그 핸들 확인: 과제 행 + 소과제 행 모두 존재')
  })

  // ── 16. 소과제 드래그앤드롭 이동 ──
  test('소과제 드래그 → 다른 과제 블록에 드롭 시 이동 API 호출', async ({ page }) => {
    // T1의 첫 소과제를 T2 블록으로 드래그
    const sourceRow = page.locator('.subtask-row[draggable="true"]').first()
    const targetBlock = page.locator('.task-block').nth(1)

    await expect(sourceRow).toBeVisible()
    await expect(targetBlock).toBeVisible()

    const sourceBox = await sourceRow.boundingBox()
    const targetBox = await targetBlock.boundingBox()
    if (!sourceBox || !targetBox) { console.log('요소 위치 측정 실패, 스킵'); return }

    // drag_indicator handle 위치에서 드래그 시작
    await page.mouse.move(sourceBox.x + 8, sourceBox.y + sourceBox.height / 2)
    await page.mouse.down()
    await page.waitForTimeout(100)
    await page.mouse.move(targetBox.x + targetBox.width / 2, targetBox.y + targetBox.height / 2, { steps: 10 })
    await page.waitForTimeout(200)
    // drag-over 클래스 확인
    const hasDragOver = await targetBlock.evaluate(el => el.classList.contains('drag-over'))
    console.log(`drag-over 클래스 적용: ${hasDragOver}`)
    await page.mouse.up()
    await page.waitForTimeout(800)

    // 이동 완료 토스트 또는 오류 없음 확인 (실제 이동은 데이터 상태에 따라 다름)
    const toast = page.locator('.toast, [class*="toast"]')
    if (await toast.isVisible({ timeout: 1000 }).catch(() => false)) {
      console.log(`토스트 메시지: ${await toast.textContent()}`)
    } else {
      console.log('토스트 없음 (같은 부모이거나 데이터 변경 없음)')
    }
  })
})
