"""The headless Training Mode command is tested through its user interface."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_training(tmp_path, *options):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "snake.sessions.TrainQLearning", *options],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )


def test_training_resumes_saved_table_without_changing_watched_games(tmp_path):
    learning_directory = tmp_path / "learning_data"
    learning_directory.mkdir()
    table_path = learning_directory / "q_table_space_state_v2.json"
    table_path.write_text(json.dumps({
        "q_table": {}, "epsilon": 0.8, "game_trained": 3,
    }))

    records_directory = tmp_path / "records"
    records_directory.mkdir()
    record_path = records_directory / "game_records.csv"
    record_path.write_text("existing game records\n")
    replays_directory = tmp_path / "replays"
    replays_directory.mkdir()
    replay_path = replays_directory / "rule_best.json"
    replay_path.write_text("existing replay\n")

    result = run_training(
        tmp_path, "--games", "2", "--width", "4", "--height", "4",
        "--seed", "7", "--max-moves", "20",
    )

    assert result.returncode == 0, result.stderr
    saved = json.loads(table_path.read_text())
    assert saved["game_trained"] == 5
    assert saved["epsilon"] < 0.8
    assert saved["q_table"]
    assert "Games: 2" in result.stdout
    assert "Best score:" in result.stdout
    assert "Epsilon:" in result.stdout
    assert record_path.read_text() == "existing game records\n"
    assert replay_path.read_text() == "existing replay\n"
    assert not (tmp_path / "experiments").exists()


@pytest.mark.parametrize("contents", [None, "not json", json.dumps({"q_table": []})])
def test_training_rejects_missing_or_malformed_saved_table(tmp_path, contents):
    learning_directory = tmp_path / "learning_data"
    learning_directory.mkdir()
    table_path = learning_directory / "q_table_space_state_v2.json"
    if contents is not None:
        table_path.write_text(contents)

    result = run_training(tmp_path, "--games", "2", "--max-moves", "10")

    assert result.returncode != 0
    assert "Q-table" in result.stderr
    if contents is None:
        assert not table_path.exists()
    else:
        assert table_path.read_text() == contents
    assert not (tmp_path / "experiments").exists()


@pytest.mark.parametrize("options", [
    ("--games", "0"),
    ("--width", "0"),
    ("--max-moves", "0"),
])
def test_invalid_training_settings_leave_the_saved_table_alone(tmp_path, options):
    learning_directory = tmp_path / "learning_data"
    learning_directory.mkdir()
    table_path = learning_directory / "q_table_space_state_v2.json"
    original = json.dumps({"q_table": {}, "epsilon": 0.8, "game_trained": 3})
    table_path.write_text(original)

    result = run_training(tmp_path, "--games", "2", *options)

    assert result.returncode != 0
    assert "positive" in result.stderr
    assert table_path.read_text() == original
