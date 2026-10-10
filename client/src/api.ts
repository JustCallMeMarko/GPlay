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

export interface Score {
  id: number
  game_id: string
  player_name: string
  score: number
  note: string
  created_at: string
}

export interface ChatMsg {
  role: 'user' | 'assistant'
  content: string
  games?: Game[]
}

async function post<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${url} failed: ${res.status}`)
  return res.json()
}

export async function matchGames(q: MatchQuery): Promise<Game[]> {
  return (await post<{ games: Game[] }>('/api/match', q)).games
}

export async function fetchGames(): Promise<Game[]> {
  const res = await fetch('/api/games')
  if (!res.ok) throw new Error(`games failed: ${res.status}`)
  return (await res.json()).games
}

export async function fetchScores(gameId?: string): Promise<Score[]> {
  const res = await fetch(`/api/scores${gameId ? `?game_id=${gameId}` : ''}`)
  if (!res.ok) throw new Error(`scores failed: ${res.status}`)
  return (await res.json()).scores
}

export async function addScore(s: {
  game_id: string
  player_name: string
  score: number
  note?: string
}): Promise<Score> {
  return post<Score>('/api/scores', s)
}

export async function deleteScore(id: number): Promise<void> {
  const res = await fetch(`/api/scores/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`delete failed: ${res.status}`)
}

export async function bumpScore(id: number, delta: number): Promise<Score> {
  const res = await fetch(`/api/scores/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ delta }),
  })
  if (!res.ok) throw new Error(`bump failed: ${res.status}`)
  return res.json()
}

/** Parse an SSE response body, dispatching each JSON payload to onEvent. */
async function readSse(
  res: Response,
  onEvent: (payload: Record<string, unknown>) => void,
): Promise<void> {
  if (!res.ok || !res.body) throw new Error(`request failed: ${res.status}`)
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
      if (payload.done) return
      onEvent(payload)
    }
  }
}

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
  await readSse(res, (p) => p.token && onToken(p.token as string))
}

export async function streamChat(
  message: string,
  history: { role: string; content: string }[],
  onToken: (token: string) => void,
  onGames: (ids: string[]) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
    signal,
  })
  await readSse(res, (p) => {
    if (p.token) onToken(p.token as string)
    if (p.games) onGames(p.games as string[])
  })
}
