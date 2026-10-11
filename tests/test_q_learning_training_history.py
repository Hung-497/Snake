"""Each Q-table keeps a Training History of the sessions that trained it (ADR 0010)."""

import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys

from snake.bots.QLearningBot import QLearningBot
from snake.engine.GameConfig import GameConfig
from snake.engine.SnakeEngine import SnakeEngine
from snake.sessions.TrainQLearning import play_game


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OLD_TABLE = {"q_table": {}, "epsilon": 0.8, "game_trained": 3}


def run_module(tmp_path, module, *options):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, "-m", module, *options],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )


def train(tmp_path, *options):
    return run_module(
        tmp_path, "snake.sessions.TrainQLearning",
        "--width", "5", "--height", "5", "--max-moves", "30", *options,
    )


def train_ok(tmp_path, *options):
    """Run training that must succeed, showing its error if it does not."""
    result = train(tmp_path, *options)
    assert result.returncode == 0, result.stderr
    return result


def read_table(path):
    return json.loads(Path(path).read_text())


def test_new_table_run_records_one_command_session(tmp_path):
    result = train(
        tmp_path, "--new-table", "--q-table", "table.json", "--games", "3", "--seed", "7",
    )

    assert result.returncode == 0, result.stderr
    saved = read_table(tmp_path / "table.json")
    [entry] = saved["training_history"]
    assert entry["source"] == "train_command"
    assert entry["started_from"] == "empty"
    assert entry["seed"] == 7
    assert entry["board"] == {"width": 5, "height": 5}
    assert entry["max_moves"] == 30
    assert entry["learning"] == {
        "learning_rate": 0.1, "discount_rate": 0.9,
        "epsilon_decay": 0.997, "min_epsilon": 0.05,
    }
    assert entry["games_at_start"] == 0
    assert entry["games_at_end"] == 3 == saved["game_trained"]
    assert entry["epsilon_at_start"] == 1.0
    assert entry["epsilon_at_end"] == saved["epsilon"]
    assert set(entry["code"]) == {"git_commit", "source_sha256"}
    assert entry["python_version"] == platform.python_version()
    assert entry["started_at"] <= entry["ended_at"]
    assert entry["best_score"] >= entry["average_score"] >= 0
    assert 0 <= entry["move_limit_games"] <= 3


def test_each_run_adds_a_session_and_keeps_earlier_ones(tmp_path):
    train_ok(tmp_path, "--new-table", "--q-table", "table.json", "--games", "2", "--seed", "1")
    first = read_table(tmp_path / "table.json")["training_history"][0]

    result = train(tmp_path, "--q-table", "table.json", "--games", "1", "--seed", "2")

    assert result.returncode == 0, result.stderr
    history = read_table(tmp_path / "table.json")["training_history"]
    assert history[0] == first
    assert history[1]["started_from"] == "existing"
    assert history[1]["seed"] == 2
    assert history[1]["games_at_start"] == 2
    assert history[1]["games_at_end"] == 3


def test_session_is_up_to_date_after_every_save(tmp_path):
    table_path = tmp_path / "table.json"
    engine = SnakeEngine(
        GameConfig(5, 5, 25), start_position=None, random_source=random.Random(3),
    )
    bot = QLearningBot(
        engine, random_source=random.Random(4), q_table_file=str(table_path),
        session={"source": "train_command", "seed": 3, "max_moves": 30},
    )

    scores = []
    move_limit_games = 0
    for game_number in range(1, 5):
        if game_number > 1:
            engine.reset()
        play_game(engine, bot, 30)
        scores.append(engine.score)
        move_limit_games += int(not engine.game_over)

        saved = read_table(table_path)
        [entry] = saved["training_history"]
        assert entry["games_at_end"] == game_number == saved["game_trained"]
        assert entry["epsilon_at_end"] == saved["epsilon"]
        assert entry["average_score"] == sum(scores) / len(scores)
        assert entry["best_score"] == max(scores)
        assert entry["move_limit_games"] == move_limit_games


def test_a_broken_history_is_refused_and_left_alone(tmp_path):
    table_path = tmp_path / "broken.json"
    table_path.write_text(json.dumps({**OLD_TABLE, "training_history": "oops"}))
    before = table_path.read_text()

    result = train(tmp_path, "--q-table", "broken.json", "--games", "1")

    assert result.returncode != 0
    assert "missing or malformed" in result.stderr
    assert table_path.read_text() == before


def test_earlier_games_without_history_are_recorded_once_as_unrecorded(tmp_path):
    table_path = tmp_path / "old.json"
    table_path.write_text(json.dumps(OLD_TABLE))

    train_ok(tmp_path, "--q-table", "old.json", "--games", "2")
    train_ok(tmp_path, "--q-table", "old.json", "--games", "1")

    saved = read_table(table_path)
    unrecorded, first, second = saved["training_history"]
    assert unrecorded == {"source": "unrecorded", "games": 3}
    assert first["games_at_start"] == 3
    assert first["games_at_end"] == 5
    assert second["source"] == "train_command"
    assert second["games_at_end"] == 6 == saved["game_trained"]


def test_a_table_with_no_games_has_nothing_unrecorded(tmp_path):
    table_path = tmp_path / "empty.json"
    table_path.write_text(json.dumps({**OLD_TABLE, "game_trained": 0}))

    train_ok(tmp_path, "--q-table", "empty.json", "--games", "1")

    [entry] = read_table(table_path)["training_history"]
    assert entry["source"] == "train_command"


def experiment(tmp_path, *options):
    return run_module(
        tmp_path, "snake.sessions.RunExperiment",
        "--games", "1", "--width", "5", "--height", "5", "--max-moves", "30", *options,
    )


def saved_report(tmp_path):
    return json.loads(next((tmp_path / "experiments").glob("*.json")).read_text())


def test_report_copies_the_training_history_of_each_q_table(tmp_path):
    train_ok(tmp_path, "--new-table", "--q-table", "v2.json", "--games", "2")
    train_ok(
        tmp_path, "--bot", "q_learning_v3", "--new-table", "--q-table", "v3.json",
        "--games", "1",
    )

    result = experiment(
        tmp_path, "--bots", "q_learning", "q_learning_v3",
        "--q-table", "v2.json", "--q-table-v3", "v3.json",
    )

    assert result.returncode == 0, result.stderr
    report = saved_report(tmp_path)
    for bot_mode, table in (("q_learning", "v2.json"), ("q_learning_v3", "v3.json")):
        expected = read_table(tmp_path / table)["training_history"]
        assert report[bot_mode]["training_history"] == expected
        assert report[bot_mode]["table_path"] == table


def test_report_lists_no_history_for_an_older_table(tmp_path):
    (tmp_path / "old.json").write_text(json.dumps(OLD_TABLE))

    result = experiment(tmp_path, "--bots", "q_learning", "--q-table", "old.json")

    assert result.returncode == 0, result.stderr
    assert saved_report(tmp_path)["q_learning"]["training_history"] == []
