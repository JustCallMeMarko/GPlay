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


def test_games_catalog():
    r = client().get("/api/games")
    assert r.status_code == 200
    games = r.json()["games"]
    assert len(games) >= 25
    assert all({"id", "name", "summary"} <= set(g) for g in games)


def _read_chat_events(r):
    events = []
    for line in r.iter_lines():
        if line.startswith("data: "):
            payload = json.loads(line[6:])
            if payload.get("done"):
                break
            events.append(payload)
    return events


def test_chat_game_related_suggests_games():
    with client().stream(
        "POST",
        "/api/chat",
        json={"message": "we want to play a game with a ball outside", "history": []},
    ) as r:
        assert r.status_code == 200
        events = _read_chat_events(r)
        text = "".join(e.get("token", "") for e in events)
        assert text.strip()
        game_events = [e for e in events if "games" in e]
        assert game_events, "expected a games suggestion event"


def test_chat_offtopic_refused():
    with client().stream(
        "POST",
        "/api/chat",
        json={"message": "what is the derivative of x^2?", "history": []},
    ) as r:
        events = _read_chat_events(r)
        text = "".join(e.get("token", "") for e in events)
        assert text.strip()
        assert not any("games" in e for e in events)


def test_scores_roundtrip():
    c = client()
    r = c.post(
        "/api/scores",
        json={"game_id": "tag-classic", "player_name": "Maya", "score": 12, "note": "3 tags"},
    )
    assert r.status_code == 201
    entry = r.json()
    assert entry["player_name"] == "Maya"

    r = c.get("/api/scores?game_id=tag-classic")
    assert any(s["id"] == entry["id"] for s in r.json()["scores"])

    r = c.delete(f"/api/scores/{entry['id']}")
    assert r.status_code == 204
    r = c.get("/api/scores?game_id=tag-classic")
    assert not any(s["id"] == entry["id"] for s in r.json()["scores"])


def test_score_unknown_game_404():
    r = client().post("/api/scores", json={"game_id": "nope", "player_name": "x", "score": 1})
    assert r.status_code == 404


def test_parse_pick_line():
    from app.llm import _parse_pick_line, GAME_PICK_MARKER

    valid = {"tag-classic", "hopscotch", "frisbee-golf"}
    # marker alone on a line
    visible, ids = _parse_pick_line(f"{GAME_PICK_MARKER} tag-classic,hopscotch,bad-id", valid)
    assert visible == ""
    assert ids == ["tag-classic", "hopscotch"]
    # marker embedded after visible text
    visible, ids = _parse_pick_line(f"Great picks! {GAME_PICK_MARKER} frisbee-golf", valid)
    assert visible == "Great picks! "
    assert ids == ["frisbee-golf"]
    # no marker
    assert _parse_pick_line("just text", valid) == ("just text", [])


def test_score_patch_delta():
    c = client()
    r = c.post("/api/scores", json={"game_id": "tag-classic", "player_name": "Team A", "score": 0})
    sid = r.json()["id"]
    r = c.patch(f"/api/scores/{sid}", json={"delta": 1})
    assert r.status_code == 200 and r.json()["score"] == 1
    r = c.patch(f"/api/scores/{sid}", json={"delta": -1})
    assert r.json()["score"] == 0
    assert c.patch("/api/scores/99999", json={"delta": 1}).status_code == 404
    c.delete(f"/api/scores/{sid}")
