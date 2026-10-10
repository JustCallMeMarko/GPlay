import { Play, Users } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import type { Game } from '@/api'

const ENERGY_STYLES: Record<string, string> = {
  low: 'bg-sky-500/15 text-sky-300',
  medium: 'bg-amber-500/15 text-amber-300',
  high: 'bg-rose-500/15 text-rose-300',
}

export function GameCard({ game, onPlay }: { game: Game; onPlay?: (g: Game) => void }) {
  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base">{game.name}</CardTitle>
          <Badge className={`capitalize ${ENERGY_STYLES[game.energy] ?? ''}`} variant="secondary">
            {game.energy}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 pb-3">
        <p className="text-sm text-muted-foreground">{game.summary}</p>
      </CardContent>
      <CardFooter className="flex items-center justify-between pt-0">
        <span className="flex items-center gap-1 text-xs text-muted-foreground">
          <Users className="h-3.5 w-3.5" />
          {game.min_players}–{game.max_players}
          <span className="ml-2">
            {game.equipment.length ? game.equipment.join(', ') : 'no equipment'}
          </span>
        </span>
        {onPlay && (
          <Button size="sm" onClick={() => onPlay(game)}>
            <Play className="h-3.5 w-3.5" /> Play
          </Button>
        )}
      </CardFooter>
    </Card>
  )
}
