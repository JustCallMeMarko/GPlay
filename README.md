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
                                           '--local HTTP--> [ Ollama: gemma-2-2b-it ]
```

## Quick start

### 1. Backend

```bash
cd server
uv venv && uv pip install -e . --group dev   # or: pip install fastapi 'uvicorn[standard]' httpx
uv run uvicorn app.main:app --reload --port 8000
```

The SQLite dataset (29 seeded games) is created automatically on first run.

### 2. Frontend

```bash
cd client
npm install
npm run dev    # http://localhost:5173, proxies /api -> :8000
```

### 3. Local AI (optional but recommended)

```bash
ollama serve
ollama pull gemma-2-2b-it
```

If Ollama or the model isn't running, `/api/rules` falls back to streaming the
built-in rules — the app works end-to-end either way.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/meta` | GET | Equipment options + area labels |
| `/api/match` | POST | `{players, equipment[], area}` → top matching games |
| `/api/rules` | POST | Same + `game_ids[]` → SSE stream of markdown tokens |
| `/api/health` | GET | Liveness |

## Tests

```bash
cd server && uv run pytest
cd client && npm run lint && npm run build
```

## Tech stack

React 19 · Vite · Tailwind CSS 4 · lucide-react · react-markdown · FastAPI · SQLite · Ollama (Gemma 2B)
