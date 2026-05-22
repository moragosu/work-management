import axios from 'axios'

function extractUploadUrls(text) {
  const urls = new Set()
  for (const m of (text || '').matchAll(/!\[.*?\]\(([^)]+)\)/g))
    if (m[1].startsWith('/uploads/')) urls.add(m[1])
  for (const m of (text || '').matchAll(/src="([^"]+)"/g))
    if (m[1].startsWith('/uploads/')) urls.add(m[1])
  return urls
}

async function deleteUrl(url) {
  const filename = url.split('/').pop()
  await axios.delete(`/api/upload/${filename}`)
}

// 이전/이후 텍스트를 비교해 제거된 업로드 이미지 삭제
export async function deleteOrphanedImages(oldText, newText) {
  const newUrls = extractUploadUrls(newText)
  const removed = [...extractUploadUrls(oldText)].filter(u => !newUrls.has(u))
  console.log('[이미지정리] 이전:', [...extractUploadUrls(oldText)], '→ 삭제대상:', removed)
  const results = await Promise.allSettled(removed.map(deleteUrl))
  results.forEach((r, i) => {
    if (r.status === 'rejected') console.warn('[이미지 삭제 실패]', removed[i], r.reason?.response?.status, r.reason?.message)
    else console.log('[이미지정리] 삭제 성공:', removed[i])
  })
}

// 텍스트 내 모든 업로드 이미지 삭제 (항목 삭제 시)
export async function deleteAllImages(...texts) {
  const urls = new Set()
  texts.forEach(t => extractUploadUrls(t).forEach(u => urls.add(u)))
  const list = [...urls]
  console.log('[이미지정리] 전체삭제 대상:', list)
  const results = await Promise.allSettled(list.map(deleteUrl))
  results.forEach((r, i) => {
    if (r.status === 'rejected') console.warn('[이미지 삭제 실패]', list[i], r.reason?.response?.status, r.reason?.message)
    else console.log('[이미지정리] 삭제 성공:', list[i])
  })
}
