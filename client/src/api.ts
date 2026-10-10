export interface Game {
  id: string
  name: string
  min_players: number
  max_players: number
  equipment: string[]
  areas: string[]
  energy: string
  summary: string
}

export interface MatchQuery {
  players: number
  equipment: string[]
  area: string
}

export async function matchGames(q: MatchQuery): Promise<Game[]> {
  const res = await fetch('/api/match', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(q),
  })
  if (!res.ok) throw new Error(`match failed: ${res.status}`)
  return (await res.json()).games
}

/** Stream rules via SSE from POST /api/rules. Calls onToken per chunk,
 * resolves when the server sends done or the stream ends. */
export async function streamRules(
  q: MatchQuery & { game_ids: string[] },
  onToken: (token: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch('/api/rules', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(q),
    signal,
  })
  if (!res.ok || !res.body) throw new Error(`rules failed: ${res.status}`)

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''
    for (const evt of events) {
      const line = evt.split('\n').find((l) => l.startsWith('data: '))
      if (!line) continue
      const payload = JSON.parse(line.slice(6))
      if (payload.token) onToken(payload.token)
      if (payload.done) return
    }
  }
}
