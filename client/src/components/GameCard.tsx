import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Play, Trophy, Users } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { Game } from '@/api'

const ENERGY_STYLES: Record<string, string> = {
  low: 'bg-sky-500/15 text-sky-300',
  medium: 'bg-amber-500/15 text-amber-300',
  high: 'bg-rose-500/15 text-rose-300',
}

interface Props {
  game: Game
  onPlay?: (g: Game) => void
  onScore?: (g: Game) => void
  /** Catalog mode: show stored rules + tags inline. */
  full?: boolean
}

export function GameCard({ game, onPlay, onScore, full }: Props) {
  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base">{game.name}</CardTitle>
          <Badge className={`capitalize ${ENERGY_STYLES[game.energy] ?? ''}`} variant="secondary">
            {game.energy}
          </Badge>
        </div>
        {full && (
          <div className="flex flex-wrap gap-1 pt-1">
            {game.tags?.map((t) => (
              <Badge key={t} variant="outline" className="text-[10px]">
                {t}
              </Badge>
            ))}
          </div>
        )}
      </CardHeader>
      <CardContent className="flex-1 pb-3">
        <p className="text-sm text-muted-foreground">{game.summary}</p>
        {full && game.rules && (
          <ScrollArea className="mt-3 h-44 rounded-md border bg-muted/30 p-3">
            <div className="prose prose-xs max-w-none text-foreground dark:prose-invert">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{game.rules}</ReactMarkdown>
            </div>
          </ScrollArea>
        )}
      </CardContent>
      <CardFooter className="flex items-center justify-between pt-0">
        <span className="flex items-center gap-1 text-xs text-muted-foreground">
          <Users className="h-3.5 w-3.5" />
          {game.min_players}–{game.max_players}
          <span className="ml-2">
            {game.equipment.length ? game.equipment.join(', ') : 'no equipment'}
          </span>
        </span>
        <div className="flex gap-1">
          {onScore && (
            <Button size="sm" variant="outline" onClick={() => onScore(game)}>
              <Trophy className="h-3.5 w-3.5" />
            </Button>
          )}
          {onPlay && (
            <Button size="sm" onClick={() => onPlay(game)}>
              <Play className="h-3.5 w-3.5" /> Play
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  )
}
