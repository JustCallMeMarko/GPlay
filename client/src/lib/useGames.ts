import { useEffect, useState } from 'react'
import { fetchGames, type Game } from '@/api'

let cache: Game[] | null = null

export function useGames() {
  const [games, setGames] = useState<Game[] | null>(cache)
  const [error, setError] = useState(false)
  useEffect(() => {
    if (cache) return
    fetchGames()
      .then((g) => {
        cache = g
        setGames(g)
      })
      .catch(() => setError(true))
  }, [])
  return { games, error }
}
