import { parseIds } from './parseIds.js'

export function getTaskMembers(taskId, staffList) {
  return staffList.filter(s => parseIds(s.selected_tasks).includes(taskId))
}

// 과제(모과제+소과제 전체)에 배정된 인력 — 중복 제거
export function getAllTaskMembers(task, staffList) {
  const ids = new Set([task.id, ...(task.sub_tasks || []).map(st => st.id)])
  return staffList.filter(s => parseIds(s.selected_tasks).some(id => ids.has(id)))
}
