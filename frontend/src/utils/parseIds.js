/**
 * 쉼표로 구분된 ID 문자열을 배열로 파싱합니다.
 * e.g. "T1, T2, T3" → ["T1", "T2", "T3"]
 */
export function parseIds(str) {
  if (!str) return []
  return str.split(',').map(id => id.trim()).filter(Boolean)
}
