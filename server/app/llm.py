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
MODEL = os.environ.get("GPLAY_MODEL", "gemma-2-2b-it")


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
    text += "> 💡 Tip: Start Ollama (`ollama serve` + `ollama pull gemma-2-2b-it`) and restart the server for AI-tailored rules.\n"
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
