import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Loader2, Minus, Plus, Trophy, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { addScore, bumpScore, deleteScore, fetchScores, type Score } from '@/api'
import { useGames } from '@/lib/useGames'

// Distinct tile colors assigned in order to each player/team.
const TILE_COLORS = [
  'bg-emerald-600 hover:bg-emerald-500',
  'bg-sky-600 hover:bg-sky-500',
  'bg-violet-600 hover:bg-violet-500',
  'bg-rose-600 hover:bg-rose-500',
  'bg-amber-600 hover:bg-amber-500',
  'bg-teal-600 hover:bg-teal-500',
  'bg-fuchsia-600 hover:bg-fuchsia-500',
  'bg-lime-600 hover:bg-lime-500',
]

export default function Scoreboard() {
  const { games } = useGames()
  const [params, setParams] = useSearchParams()
  const [gameId, setGameId] = useState(params.get('game') ?? '')
  const [scores, setScores] = useState<Score[] | null>(null)
  const [name, setName] = useState('')
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    if (!gameId) {
      setScores(null)
      return
    }
    setParams({ game: gameId }, { replace: true })
    fetchScores(gameId).then(setScores).catch(() => setScores([]))
  }, [gameId, setParams])

  async function addPlayer() {
    if (!gameId || !name.trim()) return
    setAdding(true)
    try {
      const entry = await addScore({ game_id: gameId, player_name: name, score: 0 })
      setScores((s) => [...(s ?? []), entry])
      setName('')
    } finally {
      setAdding(false)
    }
  }

  async function bump(s: Score, delta: number) {
    // Optimistic update
    setScores((list) =>
      (list ?? []).map((x) => (x.id === s.id ? { ...x, score: x.score + delta } : x)),
    )
    try {
      const updated = await bumpScore(s.id, delta)
      setScores((list) => (list ?? []).map((x) => (x.id === s.id ? updated : x)))
    } catch {
      setScores((list) =>
        (list ?? []).map((x) => (x.id === s.id ? { ...x, score: x.score - delta } : x)),
      )
    }
  }

  async function remove(id: number) {
    await deleteScore(id)
    setScores((s) => s?.filter((x) => x.id !== id) ?? null)
  }

  const ranked = [...(scores ?? [])].sort((a, b) => b.score - a.score)

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="mb-1 flex items-center gap-2 text-2xl font-bold">
        <Trophy className="h-6 w-6 text-amber-500" /> Scoreboard
      </h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Pick a game, add players or teams, then tap a box to score a point.
      </p>

      <div className="mb-6 flex flex-wrap gap-1.5">
        {games?.map((g) => (
          <Button
            key={g.id}
            size="sm"
            variant={gameId === g.id ? 'default' : 'outline'}
            onClick={() => setGameId(g.id)}
          >
            {g.name}
          </Button>
        ))}
      </div>

      {!gameId && (
        <p className="text-muted-foreground">Pick a game above to start scoring.</p>
      )}

      {gameId && (
        <>
          <div className="mb-6 flex gap-2">
            <Input
              placeholder="Player or team name…"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addPlayer()}
              className="w-64"
            />
            <Button onClick={addPlayer} disabled={adding || !name.trim()}>
              {adding ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              Add
            </Button>
          </div>

          {scores === null ? (
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          ) : scores.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No players yet — add a name above and their box appears.
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
              {ranked.map((s, i) => (
                <div key={s.id} className="relative">
                  <button
                    onClick={() => bump(s, 1)}
                    className={`flex h-32 w-full flex-col items-center justify-center rounded-2xl text-white shadow-lg transition active:scale-95 ${
                      TILE_COLORS[i % TILE_COLORS.length]
                    }`}
                  >
                    <span className="max-w-full truncate px-2 text-sm font-semibold">
                      {s.player_name}
                    </span>
                    <span className="text-4xl font-extrabold tabular-nums">{s.score}</span>
                    <span className="text-xs opacity-70">tap to score</span>
                  </button>
                  <div className="absolute right-1.5 top-1.5 flex gap-1">
                    <button
                      onClick={() => bump(s, -1)}
                      className="rounded-full bg-black/30 p-1 text-white/90 transition hover:bg-black/50"
                      title="Minus one point"
                    >
                      <Minus className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => remove(s.id)}
                      className="rounded-full bg-black/30 p-1 text-white/90 transition hover:bg-black/50"
                      title="Remove player"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
