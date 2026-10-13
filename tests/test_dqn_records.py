"""DQN games played in Live Training are saved as Records, like any Play game."""

import pytest


pytest.importorskip("torch")

from snake.engine.GameConfig import GameConfig
from snake.sessions.LiveTraining import start_live_training
from snake.sessions.LiveTrainingSession import LiveTrainingSession
from snake.sessions.SessionSettings import SessionSettings
from snake.storage.RecordManager import RecordManager
from snake.ui.RecordsBrowser import RecordsBrowser


# The columns that depend on the wall clock, not on the games themselves.
CLOCK_COLUMNS = ("date_time", "game_time", "session_time")


class FakeClock:
    """A clock that moves forward one second every time it is read."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        self.now += 1.0
        return self.now


def make_session(tmp_path, name="records.csv", width=6, height=6, max_moves=60, seed=7):
    return LiveTrainingSession(
        GameConfig(width, height, 20), seed=seed, max_moves=max_moves,
        checkpoint_path=tmp_path / "save.pt",
        record_manager=RecordManager(str(tmp_path / name)), speed_delay=5,
    )


def play_games(session, games):
    while session.stats().games_played < games:
        session.make_move()


def records(session):
    return session.record_manager.read_game_records()


def test_each_finished_game_adds_one_dqn_record(tmp_path):
    session = make_session(tmp_path)

    play_games(session, 3)

    rows = records(session)
    assert len(rows) == 3
    assert [row["player"] for row in rows] == ["dqn", "dqn", "dqn"]
    assert [row["score"] for row in rows] == [str(score) for score in session.scores]
    assert [row["games_played"] for row in rows] == ["1", "2", "3"]
    last = rows[-1]
    assert (last["board_width"], last["board_height"], last["speed_delay"]) == ("6", "6", "5")
    assert last["best_score"] == str(max(session.scores))
    assert float(last["average_score"]) == pytest.approx(session.stats().average_score)
    assert int(last["total_moves"]) > 0


def test_a_collision_is_recorded_as_died(tmp_path):
    session = make_session(tmp_path, max_moves=5000)

    play_games(session, 3)

    assert {row["outcome"] for row in records(session)} == {"died"}


def test_a_game_stopped_at_the_move_limit_has_an_unknown_outcome(tmp_path):
    session = make_session(tmp_path, width=20, height=20, max_moves=3)

    play_games(session, 2)

    assert [row["outcome"] for row in records(session)] == ["", ""]


def test_filling_the_board_is_recorded_as_won(tmp_path):
    # On a 2 x 1 board, eating the only food fills the board.
    session = make_session(tmp_path, width=2, height=1, max_moves=10, seed=3)

    play_games(session, 5)

    rows = records(session)
    assert "won" in {row["outcome"] for row in rows}
    assert all(row["outcome"] == "won" for row in rows if row["score"] == "1")


def test_background_play_records_the_same_games_as_one_move_at_a_time(tmp_path):
    one_at_a_time = make_session(tmp_path, name="live.csv")
    in_batches = make_session(tmp_path, name="background.csv")

    play_games(one_at_a_time, 3)
    while in_batches.stats().games_played < 3:
        in_batches.make_moves_for(25.0, clock=FakeClock())

    def without_clock(rows):
        return [{key: value for key, value in row.items() if key not in CLOCK_COLUMNS}
                for row in rows[:3]]

    assert without_clock(records(in_batches)) == without_clock(records(one_at_a_time))


def test_opening_live_training_records_with_the_settings_speed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")
    settings.select_speed("Normal")

    session = start_live_training(settings, checkpoint_path=tmp_path / "save.pt")
    play_games(session, 1)

    row = RecordManager().read_game_records()[0]
    assert row["player"] == "dqn"
    assert row["speed_delay"] == str(settings.speed_delay_for("dqn"))


def test_dqn_records_are_compared_under_the_board_and_speed_filters(tmp_path):
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")
    settings.select_speed("Normal")
    session = LiveTrainingSession(
        settings.build_game_config(), seed=7, max_moves=200,
        checkpoint_path=tmp_path / "save.pt",
        record_manager=RecordManager(str(tmp_path / "records.csv")),
        speed_delay=settings.speed_delay_for("dqn"),
    )
    play_games(session, 2)

    browser = RecordsBrowser(record_manager=session.record_manager, settings=settings)
    browser.load()
    dqn_rows = [row for row in browser.player_statistics() if row["player"] == "dqn"]
    browser.select_speed("Fast")
    after_other_speed = [row for row in browser.player_statistics() if row["player"] == "dqn"]

    assert len(dqn_rows) == 1 and dqn_rows[0]["games"] == 2
    assert after_other_speed == []
