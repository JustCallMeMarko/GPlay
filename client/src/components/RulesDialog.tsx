import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Loader2, Trophy } from 'lucide-react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { streamRules, type Game } from '@/api'

interface Props {
  game: Game | null
  onClose: () => void
  onScore?: (g: Game) => void
}

export function RulesDialog({ game, onClose, onScore }: Props) {
  const [rules, setRules] = useState('')
  const [streaming, setStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    abortRef.current?.abort()
    setRules('')
    if (!game) return
    const ctrl = new AbortController()
    abortRef.current = ctrl
    setStreaming(true)
    streamRules(
      {
        players: Math.min(6, game.max_players),
        equipment: game.equipment.length ? game.equipment : ['None'],
        area: game.areas[0] ?? 'grass',
        game_ids: [game.id],
      },
      (t) => setRules((r) => r + t),
      ctrl.signal,
    )
      .catch(() => setRules((r) => r || 'Could not load rules — is the API running?'))
      .finally(() => setStreaming(false))
    return () => ctrl.abort()
  }, [game])

  return (
    <Dialog open={!!game} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {game?.name}
            {streaming && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
          </DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="prose prose-sm max-w-none text-foreground dark:prose-invert">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{rules}</ReactMarkdown>
          </div>
        </ScrollArea>
        {onScore && game && (
          <div className="flex justify-end">
            <Button variant="outline" size="sm" onClick={() => onScore(game)}>
              <Trophy className="h-4 w-4" /> Record a score
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
