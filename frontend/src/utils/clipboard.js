export async function copyToClipboard(text) {
  // HTTPS 환경
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch {}
  }

  // HTTP 환경 fallback — execCommand
  try {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.cssText = 'position:absolute;left:-9999px;top:0'
    document.body.appendChild(ta)
    ta.focus()
    ta.select()
    const ok = document.execCommand('copy')
    document.body.removeChild(ta)
    if (ok) return true
  } catch {}

  return false
}
