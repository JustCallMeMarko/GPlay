import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GameCard } from '@/components/GameCard'
import { RulesDialog } from '@/components/RulesDialog'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useGames } from '@/lib/useGames'
import type { Game } from '@/api'

const AREAS: { key: string; label: string }[] = [
  { key: '', label: 'All areas' },
  { key: 'grass', label: 'Grass' },
  { key: 'hard_ground', label: 'Hard ground' },
  { key: 'small_yard', label: 'Small yard' },
  { key: 'indoor', label: 'Indoor' },
]

export default function Catalog() {
  const { games, error } = useGames()
  const [query, setQuery] = useState('')
  const [area, setArea] = useState('')
  const [rulesGame, setRulesGame] = useState<Game | null>(null)
  const navigate = useNavigate()

  const filtered = useMemo(() => {
    if (!games) return []
    return games.filter(
      (g) =>
        (!area || g.areas.includes(area)) &&
        (g.name + g.summary + g.equipment.join(' '))
          .toLowerCase()
          .includes(query.toLowerCase()),
    )
  }, [games, query, area])

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <h1 className="mb-1 text-2xl font-bold">Games Catalog</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Every game in the local library — hit Play for rules.
      </p>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <Input
          placeholder="Search games or equipment…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-64"
        />
        <div className="flex flex-wrap gap-1.5">
          {AREAS.map((a) => (
            <Badge
              key={a.key}
              variant={area === a.key ? 'default' : 'outline'}
              className="cursor-pointer"
              onClick={() => setArea(a.key)}
            >
              {a.label}
            </Badge>
          ))}
        </div>
      </div>

      {error && (
        <p className="text-sm text-rose-600">Could not load games — is the API running?</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {!games
          ? Array.from({ length: 9 }).map((_, i) => <Skeleton key={i} className="h-40" />)
          : filtered.map((g) => <GameCard key={g.id} game={g} onPlay={setRulesGame} />)}
      </div>
      {games && !filtered.length && (
        <p className="mt-8 text-center text-muted-foreground">No games match.</p>
      )}

      <RulesDialog
        game={rulesGame}
        onClose={() => setRulesGame(null)}
        onScore={(g) => navigate(`/scoreboard?game=${g.id}`)}
      />
    </div>
  )
}
