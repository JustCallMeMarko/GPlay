import json

from fastapi.testclient import TestClient

from app.main import app


def client() -> TestClient:
    c = TestClient(app)
    c.__enter__()  # run lifespan so app.state.conn exists
    return c


def test_meta():
    r = client().get("/api/meta")
    assert r.status_code == 200
    body = r.json()
    assert "Ball" in body["equipment"]
    assert "grass" in body["areas"]


def test_match_basic():
    r = client().post(
        "/api/match",
        json={"players": 8, "equipment": ["Cones", "Ball"], "area": "grass"},
    )
    assert r.status_code == 200
    games = r.json()["games"]
    assert games, "expected at least one grass game for 8 players"
    for g in games:
        assert g["min_players"] <= 8 <= g["max_players"]
        assert "grass" in g["areas"]
        assert set(g["equipment"]).issubset({"Cones", "Ball"})


def test_match_no_equipment_only():
    r = client().post(
        "/api/match",
        json={"players": 10, "equipment": ["None"], "area": "grass"},
    )
    games = r.json()["games"]
    assert games
    for g in games:
        assert g["equipment"] == []


def test_match_players_out_of_range_excluded():
    r = client().post(
        "/api/match",
        json={"players": 2, "equipment": ["None"], "area": "indoor"},
    )
    games = r.json()["games"]
    assert all(g["min_players"] <= 2 for g in games)


def test_rules_streams_sse():
    with client().stream(
        "POST",
        "/api/rules",
        json={"players": 6, "equipment": ["None"], "area": "small_yard", "game_ids": ["tag-classic"]},
    ) as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        tokens, done = [], False
        for line in r.iter_lines():
            if not line.startswith("data: "):
                continue
            payload = json.loads(line[6:])
            if payload.get("done"):
                done = True
            else:
                tokens.append(payload["token"])
        assert done
        assert "Tag" in "".join(tokens)


def test_rules_unknown_game_falls_back_to_match():
    with client().stream(
        "POST",
        "/api/rules",
        json={"players": 5, "equipment": ["None"], "area": "grass", "game_ids": []},
    ) as r:
        text = "".join(r.iter_text())
        assert '"done": true' in text
