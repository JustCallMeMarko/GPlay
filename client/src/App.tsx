import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Sparkles,
  Users,
  MapPin,
  Dumbbell,
  Loader2,
  TreePine,
  StopCircle,
} from 'lucide-react'
import { matchGames, streamRules, type Game } from './api'

const EQUIPMENT = ['None', 'Ball', 'Chalk', 'Jump Rope', 'Frisbee', 'Cones']
const AREAS: { key: string; label: string }[] = [
  { key: 'hard_ground', label: 'Hard Ground / Driveway' },
  { key: 'grass', label: 'Grassy Field' },
  { key: 'small_yard', label: 'Small Yard' },
  { key: 'indoor', label: 'Indoor / Porch' },
]

const ENERGY_STYLES: Record<string, string> = {
  low: 'bg-sky-100 text-sky-700',
  medium: 'bg-amber-100 text-amber-700',
  high: 'bg-rose-100 text-rose-700',
}

export default function App() {
  const [players, setPlayers] = useState(6)
  const [equipment, setEquipment] = useState<string[]>(['None'])
  const [area, setArea] = useState('grass')
  const [games, setGames] = useState<Game[] | null>(null)
  const [rules, setRules] = useState('')
  const [matching, setMatching] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState('')
  const abortRef = useRef<AbortController | null>(null)
  const rulesRef = useRef<HTMLDivElement | null>(null)

  function toggleEquipment(item: string) {
    setEquipment((prev) => {
      if (item === 'None') return ['None']
      const next = prev.includes(item)
        ? prev.filter((e) => e !== item)
        : [...prev.filter((e) => e !== 'None'), item]
      return next.length ? next : ['None']
    })
  }

  async function findGames() {
    setMatching(true)
    setError('')
    setRules('')
    abortRef.current?.abort()
    setStreaming(false)
    try {
      setGames(await matchGames({ players, equipment, area }))
    } catch {
      setError('Could not reach the local API. Is the FastAPI server running on :8000?')
    } finally {
      setMatching(false)
    }
  }

  async function generateRules() {
    if (!games?.length) return
    abortRef.current?.abort()
    const ctrl = new AbortController()
    abortRef.current = ctrl
    setRules('')
    setStreaming(true)
    setError('')
    try {
      await streamRules(
        { players, equipment, area, game_ids: games.map((g) => g.id) },
        (t) => setRules((r) => r + t),
        ctrl.signal,
      )
    } catch (e) {
      if ((e as Error).name !== 'AbortError')
        setError('Rule generation failed — check the server logs.')
    } finally {
      setStreaming(false)
    }
  }

  useEffect(() => {
    if (rules && rulesRef.current)
      rulesRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [rules])

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50 via-lime-50 to-white text-slate-800">
      <div className="mx-auto max-w-5xl px-4 py-10">
        <header className="mb-8 text-center">
          <div className="mb-2 flex items-center justify-center gap-2 text-emerald-700">
            <TreePine className="h-8 w-8" />
            <h1 className="text-4xl font-extrabold tracking-tight">
              Touch Grass: Play Outside
            </h1>
          </div>
          <p className="text-slate-500">
            Tell us who's here and what you've got — we'll find the perfect
            real-world game and write the rules. 100% local, no cloud needed.
          </p>
        </header>

        <section className="mb-8 rounded-2xl border border-emerald-100 bg-white p-6 shadow-sm">
          <div className="mb-6">
            <label className="mb-2 flex items-center gap-2 font-semibold">
              <Users className="h-5 w-5 text-emerald-600" />
              Players: <span className="text-emerald-700">{players >= 30 ? '30+' : players}</span>
            </label>
            <input
              type="range"
              min={2}
              max={30}
              value={players}
              onChange={(e) => setPlayers(Number(e.target.value))}
              className="w-full accent-emerald-600"
            />
            <div className="flex justify-between text-xs text-slate-400">
              <span>2</span>
              <span>30+</span>
            </div>
          </div>

          <div className="mb-6">
            <label className="mb-2 flex items-center gap-2 font-semibold">
              <Dumbbell className="h-5 w-5 text-emerald-600" />
              Equipment on hand
            </label>
            <div className="flex flex-wrap gap-2">
              {EQUIPMENT.map((item) => {
                const active = equipment.includes(item)
                return (
                  <button
                    key={item}
                    onClick={() => toggleEquipment(item)}
                    className={`rounded-full border px-4 py-1.5 text-sm font-medium transition ${
                      active
                        ? 'border-emerald-600 bg-emerald-600 text-white'
                        : 'border-slate-200 bg-slate-50 hover:border-emerald-300'
                    }`}
                  >
                    {item}
                  </button>
                )
              })}
            </div>
          </div>

          <div className="mb-6">
            <label className="mb-2 flex items-center gap-2 font-semibold">
              <MapPin className="h-5 w-5 text-emerald-600" />
              Where are you?
            </label>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {AREAS.map((a) => (
                <button
                  key={a.key}
                  onClick={() => setArea(a.key)}
                  className={`rounded-xl border px-3 py-2 text-sm font-medium transition ${
                    area === a.key
                      ? 'border-emerald-600 bg-emerald-50 text-emerald-800'
                      : 'border-slate-200 bg-slate-50 hover:border-emerald-300'
                  }`}
                >
                  {a.label}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={findGames}
            disabled={matching}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-60"
          >
            {matching ? <Loader2 className="h-5 w-5 animate-spin" /> : <Sparkles className="h-5 w-5" />}
            {matching ? 'Finding games…' : 'Find my games'}
          </button>
          {error && <p className="mt-3 text-center text-sm text-rose-600">{error}</p>}
        </section>

        {games && (
          <section className="mb-8">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-xl font-bold">
                {games.length ? `Top ${games.length} matches` : 'No games match that setup'}
              </h2>
              {games.length > 0 && (
                <button
                  onClick={streaming ? () => abortRef.current?.abort() : generateRules}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition ${
                    streaming ? 'bg-rose-500 hover:bg-rose-600' : 'bg-emerald-600 hover:bg-emerald-700'
                  }`}
                >
                  {streaming ? (
                    <>
                      <StopCircle className="h-4 w-4" /> Stop
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" /> Get tailored rules
                    </>
                  )}
                </button>
              )}
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {games.map((g) => (
                <div
                  key={g.id}
                  className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
                >
                  <div className="mb-1 flex items-start justify-between gap-2">
                    <h3 className="font-bold">{g.name}</h3>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${ENERGY_STYLES[g.energy] ?? 'bg-slate-100'}`}
                    >
                      {g.energy}
                    </span>
                  </div>
                  <p className="mb-3 text-sm text-slate-500">{g.summary}</p>
                  <div className="text-xs text-slate-400">
                    {g.min_players}–{g.max_players} players ·{' '}
                    {g.equipment.length ? g.equipment.join(', ') : 'no equipment'}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {rules && (
          <section
            ref={rulesRef}
            className="prose prose-emerald max-w-none rounded-2xl border border-emerald-100 bg-white p-6 shadow-sm"
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{rules}</ReactMarkdown>
            {streaming && <Loader2 className="mt-2 h-4 w-4 animate-spin text-emerald-500" />}
          </section>
        )}

        <footer className="mt-10 text-center text-xs text-slate-400">
          Runs fully on-device: SQLite filtering + local Gemma via Ollama. No data leaves your machine.
        </footer>
      </div>
    </div>
  )
}
