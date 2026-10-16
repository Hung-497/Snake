"""Q Learning in Play trains its own app Q-table, exactly like the headless command."""

import json

from snake.sessions.QLearningTraining import start_q_learning_training
from snake.sessions.SessionSettings import SessionSettings
from snake.sessions.TrainQLearning import main as train_q_learning
from snake.sessions.TrainingSaves import SAVE_PATHS


def small_board_settings():
    settings = SessionSettings()
    settings.select_board_size("Small 16 x 16")
    return settings


def train_games(session, games):
    while session.bot.game_trained < games:
        session.advance_by(1.0)


def read_table(path):
    return json.loads(path.read_text())


def test_a_new_app_training_learns_exactly_like_the_headless_command(tmp_path, monkeypatch):
    # Play saves Records and Replays in the current folder.
    monkeypatch.chdir(tmp_path)
    app_table = tmp_path / "app.json"
    session = start_q_learning_training(small_board_settings(), "q_learning", table_path=app_table)
    train_games(session, 3)

    train_q_learning([
        "--new-table", "--q-table", str(tmp_path / "command.json"), "--games", "3",
        "--width", "16", "--height", "16",
    ])

    app = read_table(app_table)
    command = read_table(tmp_path / "command.json")
    assert app["q_table"] == command["q_table"]
    assert app["epsilon"] == command["epsilon"]
    assert app["game_trained"] == command["game_trained"] == 3


def test_app_training_uses_seed_0_and_the_commands_move_limit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    session = start_q_learning_training(
        small_board_settings(), "q_learning", table_path=tmp_path / "app.json",
    )

    assert session.max_moves == 5000
    assert session.bot.session["seed"] == 0
    assert session.bot.session["source"] == "app"


def test_a_new_training_stops_at_its_game_limit_and_saves_it(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app_table = tmp_path / "app.json"
    session = start_q_learning_training(
        small_board_settings(), "q_learning", table_path=app_table, game_limit=2,
    )

    train_games(session, 2)

    assert session.limit_reached()
    assert read_table(app_table)["training_history"][-1]["game_limit"] == 2


def test_continuing_keeps_the_saved_game_limit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app_table = tmp_path / "app.json"
    first = start_q_learning_training(
        small_board_settings(), "q_learning", table_path=app_table, game_limit=1,
    )
    train_games(first, 1)

    # A continued training ignores a new limit and keeps the one it started with.
    continued = start_q_learning_training(
        small_board_settings(), "q_learning", table_path=app_table, game_limit=500,
    )

    assert continued.game_limit == 1
    assert continued.limit_reached()


def test_q_learning_v3_trains_its_own_app_table():
    assert SAVE_PATHS["q_learning_v3"].name == "q_table_app_v3.json"
    assert SAVE_PATHS["q_learning"].name == "q_table_app_v2.json"
