"""Touch Grass: Play Outside — FastAPI backend."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from . import db
from .games_data import AREA_LABELS, AREAS, EQUIPMENT
from .llm import stream_rules


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.conn = db.get_conn()
    yield
    app.state.conn.close()


app = FastAPI(title="Touch Grass: Play Outside", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatchRequest(BaseModel):
    players: int = Field(ge=1, le=100)
    equipment: list[str] = []
    area: str


class RulesRequest(MatchRequest):
    game_ids: list[str] = []


@app.get("/api/meta")
def meta():
    return {"equipment": EQUIPMENT, "areas": AREA_LABELS, "area_keys": AREAS}


@app.post("/api/match")
def match(req: MatchRequest):
    games = db.filter_games(app.state.conn, req.players, req.equipment, req.area)
    return {
        "games": [
            {k: g[k] for k in ("id", "name", "min_players", "max_players", "equipment", "areas", "energy", "summary")}
            for g in games
        ]
    }


@app.post("/api/rules")
def rules(req: RulesRequest):
    games = db.get_games(app.state.conn, req.game_ids)
    if not games:
        games = db.filter_games(app.state.conn, req.players, req.equipment, req.area)
    area_label = AREA_LABELS.get(req.area, req.area)

    async def event_gen():
        async for token in stream_rules(games, req.players, req.equipment, area_label):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}
