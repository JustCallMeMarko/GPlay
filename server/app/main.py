"""Touch Grass: Play Outside — FastAPI backend."""

from __future__ import annotations

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from . import db
from .games_data import AREA_LABELS, AREAS, EQUIPMENT
from .llm import stream_rules, stream_chat


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


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = []


class ScoreRequest(BaseModel):
    game_id: str
    player_name: str = Field(min_length=1, max_length=40)
    score: int = Field(ge=-999999, le=999999)
    note: str = Field(default="", max_length=200)


def game_card(g: dict) -> dict:
    return {k: g[k] for k in ("id", "name", "min_players", "max_players", "equipment", "areas", "energy", "summary")}


@app.get("/api/meta")
def meta():
    return {"equipment": EQUIPMENT, "areas": AREA_LABELS, "area_keys": AREAS}


@app.post("/api/match")
def match(req: MatchRequest):
    games = db.filter_games(app.state.conn, req.players, req.equipment, req.area)
    return {"games": [game_card(g) for g in games]}


@app.get("/api/games")
def games():
    return {"games": [game_card(g) for g in db.list_games(app.state.conn)]}


@app.post("/api/chat")
def chat(req: ChatRequest):
    catalog = db.list_games(app.state.conn)
    history = [m.model_dump() for m in req.history]

    async def event_gen():
        async for event in stream_chat(history, req.message, catalog):
            yield f"data: {json.dumps(event)}\n\n"
        yield 'data: {"done": true}\n\n'

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/scores")
def scores(game_id: str | None = None):
    return {"scores": db.list_scores(app.state.conn, game_id)}


@app.post("/api/scores", status_code=201)
def add_score(req: ScoreRequest):
    if not db.get_games(app.state.conn, [req.game_id]):
        raise HTTPException(status_code=404, detail="unknown game_id")
    return db.add_score(app.state.conn, req.game_id, req.player_name, req.score, req.note)


class ScoreDelta(BaseModel):
    delta: int = Field(ge=-100, le=100)


@app.patch("/api/scores/{score_id}")
def update_score(score_id: int, req: ScoreDelta):
    row = app.state.conn.execute(
        "UPDATE scores SET score = score + ? WHERE id = ? RETURNING *",
        (req.delta, score_id),
    ).fetchone()
    app.state.conn.commit()
    if not row:
        raise HTTPException(status_code=404, detail="unknown score id")
    return dict(row)


@app.delete("/api/scores/{score_id}", status_code=204)
def delete_score(score_id: int):
    app.state.conn.execute("DELETE FROM scores WHERE id = ?", (score_id,))
    app.state.conn.commit()


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
