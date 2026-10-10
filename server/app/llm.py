"""Local LLM inference via Ollama (Gemma open-weight model) with an
offline fallback so the app still works before Ollama/model are set up.
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator

import httpx

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("GPLAY_MODEL", "gemma4:latest")


def build_prompt(games: list[dict], players: int, equipment: list[str], area_label: str) -> str:
    games_ctx = "\n\n".join(
        f"GAME: {g['name']}\nPlayers: {g['min_players']}-{g['max_players']}\n"
        f"Summary: {g['summary']}\nBase rules:\n{g['base_rules']}"
        for g in games
    )
    gear = ", ".join(equipment) if equipment else "no equipment"
    return f"""You are a friendly outdoor games coach. A group wants to play RIGHT NOW.

Group setup:
- Players: {players}
- Equipment on hand: {gear}
- Area: {area_label}

Candidate games (already filtered to fit):
{games_ctx}

Write a polished markdown playbook they can follow immediately:
1. Start with a one-line "## Recommended: <best game>" verdict and a 1-sentence why.
2. Then, for EACH candidate game, a "### <name>" section with:
   - **Setup:** one line (boundaries, positions, things to grab)
   - **How to play:** 3-6 crisp bullet steps, adapted to THIS group's player count, area, and equipment
   - **Win / rotate:** one line
3. End with a "> 💡 Tip:" callout adapting the games to the group (safety, scaling up/down, or fairness for mixed ages).

Keep it under 350 words. Markdown only — no preamble, no code fences."""


async def stream_ollama(prompt: str) -> AsyncIterator[str]:
    """Yield tokens from Ollama's /api/generate streaming endpoint."""
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=5.0)) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": True},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                token = data.get("response", "")
                if token:
                    yield token
                if data.get("done"):
                    break


async def stream_fallback(games: list[dict]) -> AsyncIterator[str]:
    """Deterministic rules stream when no local model is reachable."""
    best = games[0]["name"] if games else "these games"
    text = f"## Recommended: {best}\n\n"
    text += "Local AI engine is not running, so here are the built-in rules for your matches.\n\n"
    for g in games:
        text += g["base_rules"] + "\n\n"
    text += "> 💡 Tip: Start Ollama (`ollama serve` + `ollama pull gemma4:latest`) and restart the server for AI-tailored rules.\n"
    # Fake token streaming so the UI behaves identically.
    for i in range(0, len(text), 24):
        yield text[i : i + 24]
        await asyncio.sleep(0.01)


async def stream_rules(
    games: list[dict], players: int, equipment: list[str], area_label: str
) -> AsyncIterator[str]:
    try:
        async for token in stream_ollama(build_prompt(games, players, equipment, area_label)):
            yield token
    except (httpx.HTTPError, json.JSONDecodeError, OSError):
        async for token in stream_fallback(games):
            yield token


# ---------------- Chat coach ----------------

GAME_PICK_MARKER = "GAMES_PICK:"

CHAT_SYSTEM = """You are "Coach", a friendly assistant inside an app that recommends \
real-world physical games to get people playing outside. \
You ONLY discuss physical games, sports, rules, setups, and adapting games to a \
group's players/equipment/location. For ANY unrelated question (homework, code, \
news, personal advice, etc.), politely refuse in one short sentence and steer \
back to games. Keep replies short, warm, and use light markdown (bold, bullets).

Available games in the catalog (id: name — summary):
{catalog}

When you want to show the user playable game cards, end your reply with exactly one line:
GAMES_PICK: <id>,<id>,<id>
Only use ids from the catalog above. Use it when the user describes their group/\
situation and asks what to play, or when it clearly helps. Never mention the marker."""

REFUSAL = "I only chat about physical games you can play outside — want a suggestion? Tell me your group size, equipment, and where you are!"

GAME_KEYWORDS = (
    "play", "game", "sport", "rule", "tag", "ball", "outside", "field",
    "yard", "indoor", "team", "players", "group", "kids", "frisbee",
    "chalk", "rope", "cones", "score", "win", "fun", "bored", "party",
    "recess", "pe ", "gym", "exercise", "run", "catch", "hide",
)


def _build_chat_prompt(history: list[dict], message: str, catalog: list[dict]) -> str:
    cat = "\n".join(f"{g['id']}: {g['name']} — {g['summary']}" for g in catalog)
    sys = CHAT_SYSTEM.format(catalog=cat)
    convo = "".join(f"\n{('User' if m['role'] == 'user' else 'Coach')}: {m['content']}" for m in history[-10:])
    return f"{sys}\n\nConversation:{convo}\nUser: {message}\nCoach:"


def _fallback_chat(message: str, catalog: list[dict]) -> tuple[str, list[str]]:
    """Heuristic coach for when no local model is reachable."""
    text = message.lower()
    if not any(k in text for k in GAME_KEYWORDS):
        return REFUSAL, []

    # Crude extraction: pick games whose name/equipment/areas words appear,
    # otherwise default to flexible crowd-pleasers.
    scored = []
    for g in catalog:
        hay = " ".join(
            [g["name"].lower(), g["summary"].lower()] + g["equipment"] + g["areas"]
        ).lower()
        s = sum(1 for w in set(text.split()) if len(w) > 3 and w in hay)
        scored.append((s, g))
    scored.sort(key=lambda t: -t[0])
    picks = [g["id"] for s, g in scored if s > 0][:3] or [g["id"] for _, g in scored[:3]]
    names = [g["name"] for _, g in scored[: len(picks)] if g["id"] in picks]
    reply = (
        "Here are some games that fit what you described! Tap a card for rules."
        if names
        else "Tell me your group size, equipment, and where you are, and I'll pick games."
    )
    return reply, picks


GENERATE_PROMPT = """Invent ONE fun real-world physical game (not a video game, no screens).
Return ONLY a JSON object — no markdown fences, no commentary — with keys:
- "name": short catchy name
- "min_players": int (1-10)
- "max_players": int (>= min_players, <= 40)
- "equipment": array, subset of {allowed_equipment} (empty = none needed)
- "areas": array, subset of {allowed_areas}
- "energy": one of "low","medium","high"
- "summary": one sentence
- "rules": markdown with a "### <name>" heading, a **Setup:** line, 4-8 bullet steps, and a **Win:** line.

Make it something a family could learn in one minute."""


def _slugify(name: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "custom-game"


async def generate_game(existing_ids: set[str]) -> dict | None:
    """Ask the local model to invent a new game; returns a game dict or None."""
    prompt = GENERATE_PROMPT.format(
        allowed_equipment=["Ball", "Chalk", "Jump Rope", "Frisbee", "Cones"],
        allowed_areas=["hard_ground", "grass", "small_yard", "indoor"],
    )
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=5.0)) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": MODEL, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            text = resp.json().get("response", "")
    except (httpx.HTTPError, OSError):
        return None

    try:
        start, end = text.index("{"), text.rindex("}")
        data = json.loads(text[start : end + 1])
    except (ValueError, json.JSONDecodeError):
        return None

    valid_eq = {"Ball", "Chalk", "Jump Rope", "Frisbee", "Cones"}
    valid_ar = {"hard_ground", "grass", "small_yard", "indoor"}
    name = str(data.get("name") or "Custom Game")[:60]
    slug = _slugify(name)
    i = 2
    while slug in existing_ids:
        slug = f"{_slugify(name)}-{i}"
        i += 1
    return {
        "id": slug,
        "name": name,
        "min_players": max(1, int(data.get("min_players") or 2)),
        "max_players": max(1, min(40, int(data.get("max_players") or 10))),
        "equipment": [e for e in data.get("equipment", []) if e in valid_eq],
        "areas": [a for a in data.get("areas", []) if a in valid_ar] or ["grass"],
        "energy": data.get("energy") if data.get("energy") in ("low", "medium", "high") else "medium",
        "summary": str(data.get("summary") or "")[:300],
        "base_rules": str(data.get("rules") or ""),
    }


def _parse_pick_line(line: str, valid_ids: set[str]) -> tuple[str, list[str]]:
    """Split a stream line on the GAMES_PICK marker; returns (visible_text, ids)."""
    if GAME_PICK_MARKER not in line:
        return line, []
    visible, _, marker = line.partition(GAME_PICK_MARKER)
    ids = [i.strip() for i in marker.strip().split(",") if i.strip()]
    return visible, [i for i in ids if i in valid_ids][:5]


async def stream_chat(
    history: list[dict], message: str, catalog: list[dict]
) -> AsyncIterator[dict]:
    """Yield {'token': str} events then an optional {'games': [ids]}."""
    try:
        picks: list[str] = []
        valid = {g["id"] for g in catalog}
        try:
            # Filter line-by-line so a GAMES_PICK marker never leaks into the
            # chat regardless of its length or position in the stream.
            buf = ""
            async for token in stream_ollama(_build_chat_prompt(history, message, catalog)):
                buf += token
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    visible, ids = _parse_pick_line(line, valid)
                    picks.extend(i for i in ids if i not in picks)
                    if visible:
                        yield {"token": visible + "\n"}
            if buf:
                visible, ids = _parse_pick_line(buf, valid)
                picks.extend(i for i in ids if i not in picks)
                if visible:
                    yield {"token": visible}
        except (httpx.HTTPError, json.JSONDecodeError, OSError):
            reply, picks = _fallback_chat(message, catalog)
            for i in range(0, len(reply), 24):
                yield {"token": reply[i : i + 24]}
                await asyncio.sleep(0.01)
        if picks:
            yield {"games": picks}
    except Exception:  # never break the stream for chat
        yield {"token": "Coach is offline right now — try again in a moment."}
