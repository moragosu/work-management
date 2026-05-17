export function getCurrentWeekNumber() {
  const today = new Date()
  const start = new Date(today.getFullYear(), 0, 1)
  return Math.ceil(((today - start) / 86400000 + start.getDay() + 1) / 7)
}

export function getWeekDateRange(weekStr) {
  if (!weekStr) return ''
  const weekNum = parseInt(weekStr.replace('W', ''))
  const year = new Date().getFullYear()
  const jan1 = new Date(year, 0, 1)
  const startOffset = (weekNum - 1) * 7 - jan1.getDay()
  const start = new Date(year, 0, 1 + startOffset)
  const end   = new Date(year, 0, 1 + startOffset + 6)
  const fmt = d => `${d.getMonth() + 1}/${d.getDate()}`
  return `${fmt(start)} – ${fmt(end)}`
}
