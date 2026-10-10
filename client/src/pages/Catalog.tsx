import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, Sparkles } from 'lucide-react'
import { GameCard } from '@/components/GameCard'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useGames } from '@/lib/useGames'
import { generateGame } from '@/api'

export default function Catalog() {
  const { games, error, refresh } = useGames()
  const [query, setQuery] = useState('')
  const [tag, setTag] = useState('')
  const [generating, setGenerating] = useState(false)
  const [genError, setGenError] = useState('')
  const navigate = useNavigate()

  const tags = useMemo(
    () => [...new Set((games ?? []).flatMap((g) => g.tags ?? []))].sort(),
    [games],
  )

  const filtered = useMemo(() => {
    if (!games) return []
    return games.filter(
      (g) =>
        (!tag || g.tags?.includes(tag)) &&
        (g.name + g.summary + g.tags.join(' '))
          .toLowerCase()
          .includes(query.toLowerCase()),
    )
  }, [games, query, tag])

  async function onGenerate() {
    setGenerating(true)
    setGenError('')
    try {
      await generateGame()
      refresh()
    } catch (e) {
      setGenError((e as Error).message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="mb-1 flex items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Games Catalog</h1>
        <Button onClick={onGenerate} disabled={generating} variant="outline">
          {generating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4 text-emerald-400" />
          )}
          {generating ? 'Generating…' : 'Generate with AI'}
        </Button>
      </div>
      <p className="mb-2 text-sm text-muted-foreground">
        Complete games from the local library — no waiting, no loading.
      </p>
      {genError && <p className="mb-4 text-sm text-rose-400">{genError}</p>}

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <Input
          placeholder="Search games or tags…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-64"
        />
        <div className="flex flex-wrap gap-1.5">
          <Badge
            variant={tag === '' ? 'default' : 'outline'}
            className="cursor-pointer"
            onClick={() => setTag('')}
          >
            All
          </Badge>
          {tags.map((t) => (
            <Badge
              key={t}
              variant={tag === t ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setTag(tag === t ? '' : t)}
            >
              {t}
            </Badge>
          ))}
        </div>
      </div>

      {error && (
        <p className="text-sm text-rose-400">Could not load games — is the API running?</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {!games
          ? Array.from({ length: 9 }).map((_, i) => <Skeleton key={i} className="h-40" />)
          : filtered.map((g) => (
              <GameCard
                key={g.id}
                game={g}
                full
                onScore={(game) => navigate(`/scoreboard?game=${game.id}`)}
              />
            ))}
      </div>
      {games && !filtered.length && (
        <p className="mt-8 text-center text-muted-foreground">No games match.</p>
      )}
    </div>
  )
}
