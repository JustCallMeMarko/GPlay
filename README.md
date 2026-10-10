# Touch Grass: Play Outside

An open-source, local-first web app for the Hacktoberfest **"Touch Grass"** challenge.
Tell it how many people you have, what equipment is on hand, and where you are — it
instantly filters matching physical games and uses Google's open-weight **Gemma** model
(via Ollama) to stream tailored rules, setups, and adaptations as Markdown over SSE.

Zero cloud APIs, zero API fees, works fully offline.

## Architecture

```
[ React + Tailwind ] --REST/SSE--> [ FastAPI ] --filter--> [ SQLite games DB ]
                                          \
                                           '--local HTTP--> [ Ollama: gemma4:latest ]
```

## Quick start

### Docker

```bash
# Uses Ollama installed on your machine (ollama serve + ollama pull gemma4:latest)
docker compose up --build

# No local Ollama? Run everything in containers instead:
docker compose --profile containerized-ollama up --build
```

Serves the frontend at http://localhost:5173. `OLLAMA_URL`/`GPLAY_MODEL`
env vars override the defaults (`http://host.docker.internal:11434` / `gemma4:latest`).

### Manual

#### 1. Backend

```bash
cd server
uv venv && uv pip install -e . --group dev   # or: pip install fastapi 'uvicorn[standard]' httpx
uv run uvicorn app.main:app --reload --port 8000
```

The SQLite dataset (29 seeded games) is created automatically on first run.

#### 2. Frontend

```bash
cd client
npm install
npm run dev    # http://localhost:5173, proxies /api -> :8000
```

### 3. Local AI (optional but recommended)

```bash
ollama serve
ollama pull gemma4:latest
```

If Ollama or the model isn't running, `/api/rules` falls back to streaming the
built-in rules — the app works end-to-end either way.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/meta` | GET | Equipment options + area labels |
| `/api/match` | POST | `{players, equipment[], area}` → top matching games |
| `/api/games` | GET | Full game catalog |
| `/api/chat` | POST | `{message, history[]}` → SSE: tokens + `{"games": [ids]}` suggestion events; off-topic questions are refused |
| `/api/rules` | POST | Same + `game_ids[]` → SSE stream of markdown tokens |
| `/api/scores` | GET/POST/DELETE | Per-game scoreboard entries |
| `/api/health` | GET | Liveness |

## UI

shadcn sidebar with three views:

- **Home** — "Coach" chatbot: describe your group/equipment/location and it suggests playable game cards; ask rules; unrelated questions are politely refused.
- **Games Catalog** — the full local library with search + area filters; Play opens streamed rules.
- **Scoreboard** — pick any game and log scores; ranked table per game.

## Tests

```bash
cd server && uv run pytest
cd client && npm run lint && npm run build
```

## Tech stack

React 19 · Vite · Tailwind CSS 4 · lucide-react · react-markdown · FastAPI · SQLite · Ollama (gemma4:latest)
