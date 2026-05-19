// 현재 주차를 "2026-W21" 형식으로 반환
export function getCurrentWeek() {
  const today = new Date()
  const year = today.getFullYear()
  const jan1 = new Date(year, 0, 1)
  const weekNum = Math.ceil(((today - jan1) / 86400000 + jan1.getDay() + 1) / 7)
  return `${year}-W${weekNum}`
}

// "2026-W21" → "5/18 – 5/24"
export function getWeekDateRange(weekStr) {
  if (!weekStr) return ''
  const match = weekStr.match(/^(\d{4})-W(\d+)$/)
  if (!match) return weekStr
  const year = parseInt(match[1])
  const weekNum = parseInt(match[2])
  const jan1 = new Date(year, 0, 1)
  const startOffset = (weekNum - 1) * 7 - jan1.getDay()
  const start = new Date(year, 0, 1 + startOffset)
  const end   = new Date(year, 0, 1 + startOffset + 6)
  const fmt = d => `${d.getMonth() + 1}/${d.getDate()}`
  return `${fmt(start)} – ${fmt(end)}`
}

// "2026-W21" → 표시용 레이블 (현재 연도는 연도 생략: "W21", 다른 연도: "2025-W52")
export function formatWeekLabel(weekStr) {
  if (!weekStr) return weekStr
  const match = weekStr.match(/^(\d{4})-W(\d+)$/)
  if (!match) return weekStr
  const year = parseInt(match[1])
  const weekNum = parseInt(match[2])
  return year === new Date().getFullYear() ? `W${weekNum}` : `${year}-W${weekNum}`
}

// weekStr 기준 delta주 이동한 주차 반환 (연도 경계 자동 처리)
export function addWeeks(weekStr, delta) {
  if (!weekStr) return weekStr
  const match = weekStr.match(/^(\d{4})-W(\d+)$/)
  if (!match) return weekStr
  const year = parseInt(match[1])
  const weekNum = parseInt(match[2])
  const jan1 = new Date(year, 0, 1)
  const startOffset = (weekNum - 1) * 7 - jan1.getDay()
  const monday = new Date(year, 0, 1 + startOffset)
  monday.setDate(monday.getDate() + delta * 7)
  const y = monday.getFullYear()
  const s = new Date(y, 0, 1)
  const n = Math.ceil(((monday - s) / 86400000 + s.getDay() + 1) / 7)
  return `${y}-W${n}`
}
