import axios from 'axios'

function extractUploadUrls(text) {
  const urls = new Set()
  for (const m of (text || '').matchAll(/!\[.*?\]\(([^)]+)\)/g))
    if (m[1].startsWith('/uploads/')) urls.add(m[1])
  for (const m of (text || '').matchAll(/src="([^"]+)"/g))
    if (m[1].startsWith('/uploads/')) urls.add(m[1])
  return urls
}

// 이전/이후 텍스트를 비교해 제거된 업로드 이미지 삭제
export async function deleteOrphanedImages(oldText, newText) {
  const removed = [...extractUploadUrls(oldText)].filter(u => !extractUploadUrls(newText).has(u))
  await Promise.allSettled(
    removed.map(url => axios.delete(`/api/upload/${url.split('/').pop()}`))
  )
}

// 텍스트 내 모든 업로드 이미지 삭제 (항목 삭제 시)
export async function deleteAllImages(...texts) {
  const urls = new Set()
  texts.forEach(t => extractUploadUrls(t).forEach(u => urls.add(u)))
  await Promise.allSettled(
    [...urls].map(url => axios.delete(`/api/upload/${url.split('/').pop()}`))
  )
}
