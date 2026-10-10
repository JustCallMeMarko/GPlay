"""SQLite storage for the game dataset."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .games_data import GAMES

DB_PATH = Path(__file__).resolve().parent.parent / "games.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    min_players INTEGER NOT NULL,
    max_players INTEGER NOT NULL,
    equipment TEXT NOT NULL,  -- JSON array; empty = no equipment needed
    areas TEXT NOT NULL,      -- JSON array
    energy TEXT NOT NULL,
    summary TEXT NOT NULL,
    base_rules TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id TEXT NOT NULL REFERENCES games(id),
    player_name TEXT NOT NULL,
    score INTEGER NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_conn(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    if not conn.execute("SELECT 1 FROM games LIMIT 1").fetchone():
        conn.executemany(
            """INSERT INTO games
               (id, name, min_players, max_players, equipment, areas, energy, summary, base_rules)
               VALUES (:id, :name, :min_players, :max_players, :equipment, :areas, :energy, :summary, :base_rules)""",
            [
                {**g, "equipment": json.dumps(g["equipment"]), "areas": json.dumps(g["areas"])}
                for g in GAMES
            ],
        )
        conn.commit()
    return conn


def row_to_game(row: sqlite3.Row) -> dict:
    g = dict(row)
    g["equipment"] = json.loads(g["equipment"])
    g["areas"] = json.loads(g["areas"])
    return g


def list_games(conn: sqlite3.Connection) -> list[dict]:
    return [row_to_game(r) for r in conn.execute("SELECT * FROM games ORDER BY name")]


def get_games(conn: sqlite3.Connection, ids: list[str]) -> list[dict]:
    if not ids:
        return []
    placeholders = ",".join("?" for _ in ids)
    rows = conn.execute(f"SELECT * FROM games WHERE id IN ({placeholders})", ids).fetchall()
    by_id = {r["id"]: row_to_game(r) for r in rows}
    return [by_id[i] for i in ids if i in by_id]


def filter_games(
    conn: sqlite3.Connection,
    players: int,
    equipment: list[str],
    area: str,
    limit: int = 5,
) -> list[dict]:
    """Deterministic local filter: player range, area match, and required
    equipment must be a subset of what the user selected ('None' = nothing)."""
    selected = set(equipment)
    results = []
    for game in list_games(conn):
        if not (game["min_players"] <= players <= game["max_players"]):
            continue
        if area not in game["areas"]:
            continue
        required = set(game["equipment"])
        if not required.issubset(selected):
            continue
        results.append(game)
        if len(results) >= limit:
            break
    return results


def add_score(conn: sqlite3.Connection, game_id: str, player_name: str, score: int, note: str = "") -> dict:
    cur = conn.execute(
        "INSERT INTO scores (game_id, player_name, score, note) VALUES (?, ?, ?, ?)",
        (game_id, player_name.strip(), score, note.strip()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM scores WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


def list_scores(conn: sqlite3.Connection, game_id: str | None = None) -> list[dict]:
    if game_id:
        rows = conn.execute(
            "SELECT * FROM scores WHERE game_id = ? ORDER BY score DESC, created_at ASC",
            (game_id,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM scores ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]
