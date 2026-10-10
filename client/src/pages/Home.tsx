import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { SendHorizonal, TreePine } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import { GameCard } from '@/components/GameCard'
import { RulesDialog } from '@/components/RulesDialog'
import { streamChat, type ChatMsg, type Game } from '@/api'
import { useGames } from '@/lib/useGames'

const SUGGESTIONS = [
  'We are 8 people on a grassy field with just a ball — what can we play?',
  'How do the rules of Four Square work?',
  'Rainy day, 5 of us stuck on the porch with nothing. Ideas?',
]

export default function Home() {
  const [messages, setMessages] = useState<ChatMsg[]>([
    {
      role: 'assistant',
      content:
        "Hey! I'm Coach. Tell me who's here, what gear you've got, and where you are — I'll find you a real-world game. You can also ask me how any game is played.",
    },
  ])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [rulesGame, setRulesGame] = useState<Game | null>(null)
  const { games: catalog } = useGames()
  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(text?: string) {
    const msg = (text ?? input).trim()
    if (!msg || streaming) return
    setInput('')
    const history = [...messages, { role: 'user' as const, content: msg }]
    setMessages([...history, { role: 'assistant', content: '' }])
    setStreaming(true)
    const ctrl = new AbortController()
    abortRef.current = ctrl

    const append = (t: string) =>
      setMessages((ms) => {
        const out = [...ms]
        out[out.length - 1] = { ...out[out.length - 1], content: out[out.length - 1].content + t }
        return out
      })
    const attachGames = (ids: string[]) =>
      setMessages((ms) => {
        const out = [...ms]
        out[out.length - 1] = {
          ...out[out.length - 1],
          games: ids
            .map((id) => catalog?.find((g) => g.id === id))
            .filter((g): g is Game => !!g),
        }
        return out
      })

    try {
      await streamChat(msg, history.slice(0, -1), append, attachGames, ctrl.signal)
    } catch {
      append('\n\n*(connection lost — is the API running?)*')
    } finally {
      setStreaming(false)
    }
  }

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1">
        <div className="mx-auto max-w-3xl space-y-6 px-4 py-6">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                  m.role === 'user'
                    ? 'bg-emerald-600 text-white'
                    : 'bg-muted text-foreground'
                }`}
              >
                {m.role === 'assistant' ? (
                  <div className="prose prose-sm max-w-none text-foreground dark:prose-invert">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {m.content || '…'}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-sm">{m.content}</p>
                )}
                {m.games?.length ? (
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    {m.games.map((g) => (
                      <GameCard key={g.id} game={g} onPlay={setRulesGame} />
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          ))}
          {streaming && (
            <span
              className="inline-block bg-gradient-to-r from-emerald-500 via-white to-emerald-500 bg-clip-text text-sm font-semibold text-transparent"
              style={{ backgroundSize: '200% 100%', animation: 'shimmer 1.4s linear infinite' }}
            >
              Generating…
            </span>
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <div className="border-t bg-background px-4 py-3">
        {messages.length <= 1 && (
          <div className="mx-auto mb-3 flex max-w-3xl flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                className="rounded-full border px-3 py-1 text-xs text-zinc-300 transition hover:border-emerald-400 hover:text-white"
              >
                {s}
              </button>
            ))}
          </div>
        )}
        <div className="mx-auto flex max-w-3xl items-end gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                send()
              }
            }}
            placeholder="Describe your group, or ask about a game's rules…"
            className="min-h-[44px] resize-none"
            rows={1}
          />
          <Button onClick={() => send()} disabled={!input.trim() || streaming} size="icon">
            <SendHorizonal className="h-4 w-4" />
          </Button>
        </div>
        <p className="mx-auto mt-1 flex max-w-3xl items-center gap-1 text-xs text-zinc-300">
          <TreePine className="h-3 w-3" /> Coach only talks real-world games — 100% local.
        </p>
      </div>

      <RulesDialog
        game={rulesGame}
        onClose={() => setRulesGame(null)}
        onScore={(g) => navigate(`/scoreboard?game=${g.id}`)}
      />
    </div>
  )
}
