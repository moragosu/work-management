import { parseIds } from './parseIds.js'

export function getTaskMembers(taskId, staffList) {
  return staffList.filter(s => parseIds(s.selected_tasks).includes(taskId))
}
