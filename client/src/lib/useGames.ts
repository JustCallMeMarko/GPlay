import { useCallback, useEffect, useState } from 'react'
import { fetchGames, type Game } from '@/api'

let cache: Game[] | null = null

export function useGames() {
  const [games, setGames] = useState<Game[] | null>(cache)
  const [error, setError] = useState(false)

  const refresh = useCallback(() => {
    fetchGames()
      .then((g) => {
        cache = g
        setGames(g)
      })
      .catch(() => setError(true))
  }, [])

  useEffect(() => {
    if (cache) return
    refresh()
  }, [refresh])

  return { games, error, refresh }
}
