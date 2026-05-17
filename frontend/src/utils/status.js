const STATUS_BADGE = {
  '진행중': 'badge badge-blue',
  '완료':   'badge badge-green',
  '위험':   'badge badge-red',
}

export function statusBadgeClass(status) {
  return STATUS_BADGE[status] || 'badge badge-gray'
}
