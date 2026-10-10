import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Loader2, Plus, Trash2, Trophy } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { addScore, deleteScore, fetchScores, type Score } from '@/api'
import { useGames } from '@/lib/useGames'

export default function Scoreboard() {
  const { games } = useGames()
  const [params, setParams] = useSearchParams()
  const [gameId, setGameId] = useState(params.get('game') ?? '')
  const [scores, setScores] = useState<Score[] | null>(null)
  const [name, setName] = useState('')
  const [score, setScore] = useState('')
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(false)

  const game = useMemo(() => games?.find((g) => g.id === gameId), [games, gameId])

  useEffect(() => {
    if (!gameId) {
      setScores(null)
      return
    }
    setParams({ game: gameId }, { replace: true })
    fetchScores(gameId).then(setScores).catch(() => setScores([]))
  }, [gameId, setParams])

  async function submit() {
    if (!gameId || !name.trim() || score === '') return
    setSaving(true)
    try {
      const entry = await addScore({
        game_id: gameId,
        player_name: name,
        score: Number(score),
        note,
      })
      setScores((s) => [...(s ?? []), entry].sort((a, b) => b.score - a.score))
      setScore('')
      setNote('')
    } finally {
      setSaving(false)
    }
  }

  async function remove(id: number) {
    await deleteScore(id)
    setScores((s) => s?.filter((x) => x.id !== id) ?? null)
  }

  const medals = ['🥇', '🥈', '🥉']

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="mb-1 flex items-center gap-2 text-2xl font-bold">
        <Trophy className="h-6 w-6 text-amber-500" /> Scoreboard
      </h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Track results for any game — pick one and log who won.
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
        <p className="text-muted-foreground">Pick a game above to see or add scores.</p>
      )}

      {gameId && (
        <Card>
          <CardHeader>
            <CardTitle>{game?.name ?? 'Scores'}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4 flex flex-wrap gap-2">
              <Input
                placeholder="Player / team name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-48"
              />
              <Input
                placeholder="Score"
                type="number"
                value={score}
                onChange={(e) => setScore(e.target.value)}
                className="w-28"
              />
              <Input
                placeholder="Note (optional)"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                className="w-56"
              />
              <Button onClick={submit} disabled={saving || !name.trim() || score === ''}>
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                Add
              </Button>
            </div>

            {scores === null ? (
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            ) : scores.length === 0 ? (
              <p className="text-sm text-muted-foreground">No scores yet — be the first.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">#</TableHead>
                    <TableHead>Player</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead>Note</TableHead>
                    <TableHead>When</TableHead>
                    <TableHead className="w-12" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {scores.map((s, i) => (
                    <TableRow key={s.id}>
                      <TableCell>{medals[i] ?? i + 1}</TableCell>
                      <TableCell className="font-medium">{s.player_name}</TableCell>
                      <TableCell className="font-bold">{s.score}</TableCell>
                      <TableCell className="text-muted-foreground">{s.note}</TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {s.created_at.replace('T', ' ').slice(0, 16)}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => remove(s.id)}
                          title="Delete score"
                        >
                          <Trash2 className="h-4 w-4 text-muted-foreground" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
