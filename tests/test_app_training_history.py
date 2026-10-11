"""App play in Training Mode adds to the Q-table's Training History (ADR 0010)."""

import json
from pathlib import Path
import random

from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine
from snake.sessions.GameSession import GameSession


TABLE_PATH = Path("learning_data") / "q_table_space_state_v2.json"


def make_engine(seed=3):
    return SnakeEngine(
        GameConfig(5, 5, 25), start_position=None, random_source=random.Random(seed),
    )


def play_games(session, games):
    """Advance a bot session, as the Game view does each frame, until enough games end."""
    for _ in range(10_000):
        if session.games_played >= games:
            return
        session.advance_by(1.0)
    raise AssertionError("the session did not finish its games")


def read_history():
    return json.loads(TABLE_PATH.read_text())["training_history"]


def test_app_session_records_one_app_entry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    session = GameSession(make_engine(), "q_learning", speed_delay=1)

    play_games(session, 3)

    [entry] = read_history()
    assert entry["source"] == "app"
    assert entry["seed"] is None
    assert entry["max_moves"] is None
    assert entry["started_from"] == "empty"
    assert entry["board"] == {"width": 5, "height": 5}
    assert entry["games_at_end"] == 3
    assert entry["move_limit_games"] == 0


def test_each_game_view_visit_is_its_own_session(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    play_games(GameSession(make_engine(), "q_learning", speed_delay=1), 2)

    play_games(GameSession(make_engine(4), "q_learning", speed_delay=1), 1)

    first, second = read_history()
    assert first["games_at_end"] == 2
    assert second["started_from"] == "existing"
    assert second["games_at_start"] == 2
    assert second["games_at_end"] == 3


def test_a_visit_that_finishes_no_game_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    session = GameSession(make_engine(), "q_learning", speed_delay=1)

    session.advance()
    session.stop()

    assert not TABLE_PATH.exists()

