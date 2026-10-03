export async function api<T = any>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch('/api' + path, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    ...init,
  })
  if (!res.ok) throw new Error(await res.text() || res.statusText)
  if (res.status === 204) return undefined as T
  return res.json()
}

/** 从 api() 抛出的错误里取出后端 detail 文案（如“不在补货时段”），保持原样展示不改写。 */
export function errMsg(e: unknown): string {
  const raw = e instanceof Error ? e.message : String(e)
  try {
    const j = JSON.parse(raw)
    if (typeof j.detail === 'string') return j.detail
    if (Array.isArray(j.detail)) return j.detail.map((d: any) => d?.msg ?? String(d)).join('；')
  } catch { /* 非 JSON，原样返回 */ }
  return raw
}
