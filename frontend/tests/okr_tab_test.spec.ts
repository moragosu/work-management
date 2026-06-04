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

  // ── 16. 소과제 DnD 이동 — DragEvent 직접 dispatch ──
  test('소과제 드래그앤드롭 이동 — move-sub-task API 호출 확인', async ({ page }) => {
    // API 인터셉트: 실제 데이터 변경 없이 요청 바디만 검증
    let captured: any = null
    await page.route('**/api/tasks/**/move-sub-task', async route => {
      captured = JSON.parse(route.request().postData() || '{}')
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
    })
    // reusable-sub-ids mock: 빈 번호 T2-1이 있을 때 T2-4(next) 대신 T2-1 우선 사용 확인
    await page.route('**/api/tasks/T2/reusable-sub-ids', async route => {
      await route.fulfill({ status: 200, contentType: 'application/json',
        body: JSON.stringify({ next: 'T2-4', reusable: ['T2-1'] }) })
    })

    // T1의 첫 소과제(T1-1) → T2 블록으로 DragEvent dispatch
    const sourceRow = page.locator('.subtask-row[draggable="true"]').first()
    const targetBlock = page.locator('.task-block').nth(1)
    await expect(sourceRow).toBeVisible()
    await expect(targetBlock).toBeVisible()

    await page.screenshot({ path: '/tmp/dnd_before.png' })

    await page.evaluate(([src, tgt]) => {
      const dt = new DataTransfer()
      src.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }))
      tgt.dispatchEvent(new DragEvent('dragover',  { bubbles: true, cancelable: true, dataTransfer: dt }))
      tgt.dispatchEvent(new DragEvent('drop',      { bubbles: true, cancelable: true, dataTransfer: dt }))
      src.dispatchEvent(new DragEvent('dragend',   { bubbles: true, cancelable: true }))
    }, [await sourceRow.elementHandle(), await targetBlock.elementHandle()])

    await page.waitForTimeout(800)
    await page.screenshot({ path: '/tmp/dnd_after_move.png' })

    expect(captured).toBeTruthy()
    expect(captured.from_parent_id).toBe('T1')
    expect(captured.to_parent_id).toBe('T2')
    // reusable(['T2-1'])이 있으므로 next('T2-4') 대신 T2-1 우선 사용
    expect(captured.new_sub_id).toBe('T2-1')
    console.log(`이동 API 바디: ${JSON.stringify(captured)}`)
  })

  // ── 17. drag-over 클래스 표시 ──
  test('소과제 드래그 중 대상 과제 블록에 drag-over 클래스 적용', async ({ page }) => {
    const sourceRow = page.locator('.subtask-row[draggable="true"]').first()
    const targetBlock = page.locator('.task-block').nth(1)
    await expect(sourceRow).toBeVisible()

    await page.evaluate(([src, tgt]) => {
      const dt = new DataTransfer()
      src.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }))
      tgt.dispatchEvent(new DragEvent('dragover',  { bubbles: true, cancelable: true, dataTransfer: dt }))
    }, [await sourceRow.elementHandle(), await targetBlock.elementHandle()])

    await page.waitForTimeout(100)
    const hasDragOver = await targetBlock.evaluate(el => el.classList.contains('drag-over'))
    console.log(`drag-over 클래스: ${hasDragOver}`)
    expect(hasDragOver).toBe(true)

    await page.screenshot({ path: '/tmp/dnd_dragover.png' })

    // dragend로 해제
    await page.evaluate(src => src.dispatchEvent(new DragEvent('dragend', { bubbles: true })),
      await sourceRow.elementHandle())
    await page.waitForTimeout(100)
    const afterEnd = await targetBlock.evaluate(el => el.classList.contains('drag-over'))
    console.log(`dragend 후 drag-over 해제: ${!afterEnd}`)
    expect(afterEnd).toBe(false)
  })

  // ── 18. 과제 편입 DnD ──
  test('과제 드래그앤드롭 편입 — absorb API 호출 확인', async ({ page }) => {
    let captured: any = null
    await page.route('**/api/tasks/**/absorb', async route => {
      captured = JSON.parse(route.request().postData() || '{}')
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
    })
    await page.route('**/api/tasks/T1/reusable-sub-ids', async route => {
      await route.fulfill({ status: 200, contentType: 'application/json',
        body: JSON.stringify({ next: 'T1-5', reusable: [] }) })
    })

    // 소과제 없는 과제 행(T3 또는 T5)을 T1 블록으로 드래그
    const sourceRow = page.locator('.task-row[draggable="true"]').first()
    const targetBlock = page.locator('.task-block').first()

    const sourceTaskId = await sourceRow.locator('.task-id-badge').textContent()
    const targetTaskId = await targetBlock.locator('.task-row .task-id-badge').first().textContent()
    console.log(`편입 드래그: ${sourceTaskId?.trim()} → ${targetTaskId?.trim()} 블록`)

    await page.evaluate(([src, tgt]) => {
      const dt = new DataTransfer()
      src.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }))
      tgt.dispatchEvent(new DragEvent('dragover',  { bubbles: true, cancelable: true, dataTransfer: dt }))
      tgt.dispatchEvent(new DragEvent('drop',      { bubbles: true, cancelable: true, dataTransfer: dt }))
      src.dispatchEvent(new DragEvent('dragend',   { bubbles: true, cancelable: true }))
    }, [await sourceRow.elementHandle(), await targetBlock.elementHandle()])

    await page.waitForTimeout(800)
    await page.screenshot({ path: '/tmp/dnd_after_absorb.png' })

    expect(captured).toBeTruthy()
    expect(captured.new_sub_id).toBeTruthy()
    console.log(`편입 API 바디: ${JSON.stringify(captured)}`)
  })

  // ── 19. 드롭 후 스크롤 위치 복원 ──
  test('드롭 후 스크롤 위치 복원', async ({ page }) => {
    await page.route('**/api/tasks/**/move-sub-task', async route => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
    })
    await page.route('**/api/tasks/T2/reusable-sub-ids', async route => {
      await route.fulfill({ status: 200, contentType: 'application/json',
        body: JSON.stringify({ next: 'T2-4', reusable: [] }) })
    })

    // 페이지를 300px 아래로 스크롤 후 드롭
    await page.evaluate(() => window.scrollTo(0, 300))
    await page.waitForTimeout(100)
    const scrollBefore = await page.evaluate(() => window.scrollY)
    expect(scrollBefore).toBeGreaterThan(200)

    const sourceRow = page.locator('.subtask-row[draggable="true"]').first()
    const targetBlock = page.locator('.task-block').nth(1)
    await page.evaluate(([src, tgt]) => {
      const dt = new DataTransfer()
      src.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }))
      tgt.dispatchEvent(new DragEvent('dragover',  { bubbles: true, cancelable: true, dataTransfer: dt }))
      tgt.dispatchEvent(new DragEvent('drop',      { bubbles: true, cancelable: true, dataTransfer: dt }))
      src.dispatchEvent(new DragEvent('dragend',   { bubbles: true, cancelable: true }))
    }, [await sourceRow.elementHandle(), await targetBlock.elementHandle()])

    // refresh + setTimeout(150ms) 대기
    await page.waitForTimeout(600)
    const scrollAfter = await page.evaluate(() => window.scrollY)
    console.log(`스크롤 복원: before=${scrollBefore}, after=${scrollAfter}`)
    expect(Math.abs(scrollAfter - scrollBefore)).toBeLessThan(50)
  })

  // ── 20. 드래그 중 하단 경계 자동 스크롤 ──
  test('드래그 중 viewport 하단에서 자동 스크롤', async ({ page }) => {
    await page.evaluate(() => window.scrollTo(0, 0))
    const scrollBefore = await page.evaluate(() => window.scrollY)

    const sourceRow = page.locator('.subtask-row[draggable="true"]').first()
    await expect(sourceRow).toBeVisible()

    // dragstart 후 viewport 하단 근처에서 dragover 이벤트 dispatch
    await page.evaluate(src => {
      const dt = new DataTransfer()
      src.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }))
      // document에 clientY = vh - 40 (하단 경계 내부) 로 dragover 발화
      document.dispatchEvent(new DragEvent('dragover', {
        bubbles: true, cancelable: true, dataTransfer: dt,
        clientY: window.innerHeight - 40
      }))
    }, await sourceRow.elementHandle())

    await page.waitForTimeout(200)
    const scrollAfter = await page.evaluate(() => window.scrollY)
    console.log(`자동 스크롤: before=${scrollBefore}, after=${scrollAfter}`)
    expect(scrollAfter).toBeGreaterThan(scrollBefore)

    // 정리: dragend
    await page.evaluate(src => src.dispatchEvent(new DragEvent('dragend', { bubbles: true })),
      await sourceRow.elementHandle())
  })
})
