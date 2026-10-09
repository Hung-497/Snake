"""Q Learning v3 is trained and measured headlessly, next to Q Learning v2."""

import json
import os
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
V2_TABLE = json.dumps({"q_table": {}, "epsilon": 0.8, "game_trained": 3})


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
        "--games", "2", "--width", "5", "--height", "5", "--max-moves", "30",
        *options,
    )


def experiment(tmp_path, *options):
    return run_module(
        tmp_path, "snake.sessions.RunExperiment",
        "--width", "5", "--height", "5", "--seed", "7", "--max-moves", "30",
        *options,
    )


def write_v2_table(tmp_path):
    table_path = tmp_path / "learning_data" / "q_table_space_state_v2.json"
    table_path.parent.mkdir(exist_ok=True)
    table_path.write_text(V2_TABLE)
    return table_path


def test_new_table_option_creates_and_trains_an_empty_v3_table(tmp_path):
    v2_table = write_v2_table(tmp_path)

    result = train(tmp_path, "--bot", "q_learning_v3", "--new-table")

    assert result.returncode == 0, result.stderr
    saved = json.loads(
        (tmp_path / "learning_data" / "q_table_space_state_v3.json").read_text()
    )
    assert saved["feature_set"] == "v3"
    assert saved["game_trained"] == 2
    assert all(len(key.split("_")) == 12 for key in saved["q_table"])
    assert v2_table.read_text() == V2_TABLE


def test_new_table_can_be_written_to_a_chosen_path(tmp_path):
    result = train(
        tmp_path, "--bot", "q_learning_v3", "--new-table",
        "--q-table", "runs/seed_7.json",
    )

    assert result.returncode == 0, result.stderr
    saved = json.loads((tmp_path / "runs" / "seed_7.json").read_text())
    assert saved["feature_set"] == "v3"


def test_training_v3_without_a_table_is_refused(tmp_path):
    result = train(tmp_path, "--bot", "q_learning_v3")

    assert result.returncode != 0
    assert "missing or malformed" in result.stderr
    assert not (tmp_path / "learning_data").exists()


def test_new_table_never_overwrites_an_existing_table(tmp_path):
    table_path = tmp_path / "v3.json"
    table_path.write_text("keep me")

    result = train(
        tmp_path, "--bot", "q_learning_v3", "--new-table", "--q-table", str(table_path),
    )

    assert result.returncode != 0
    assert "already exists" in result.stderr
    assert table_path.read_text() == "keep me"


def test_new_table_is_only_for_q_learning_v3(tmp_path):
    result = train(tmp_path, "--new-table")

    assert result.returncode != 0
    assert "--new-table" in result.stderr


def test_experiment_compares_q_learning_versions_on_the_same_seeds(tmp_path):
    write_v2_table(tmp_path)
    assert train(tmp_path, "--bot", "q_learning_v3", "--new-table").returncode == 0

    result = experiment(
        tmp_path, "--games", "2", "--bots", "q_learning", "q_learning_v3",
    )

    assert result.returncode == 0, result.stderr
    saved = json.loads(next((tmp_path / "experiments").glob("*.json")).read_text())
    assert saved["selected_bot_modes"] == ["q_learning", "q_learning_v3"]
    assert len(saved["bots"]["q_learning_v3"]["games"]) == 2
    assert saved["q_learning"]["feature_set"] == "v2"
    assert saved["q_learning_v3"]["feature_set"] == "v3"
    assert saved["q_learning_v3"]["table_path"].endswith("q_table_space_state_v3.json")
    assert "Q Learning v3" in result.stdout


def test_experiment_uses_a_chosen_v3_table(tmp_path):
    assert train(
        tmp_path, "--bot", "q_learning_v3", "--new-table", "--q-table", "mine.json",
    ).returncode == 0

    result = experiment(tmp_path, "--bots", "q_learning_v3", "--q-table-v3", "mine.json")

    assert result.returncode == 0, result.stderr
    saved = json.loads(next((tmp_path / "experiments").glob("*.json")).read_text())
    assert saved["q_learning_v3"]["table_path"] == "mine.json"


def test_experiment_refuses_q_learning_v3_without_a_table(tmp_path):
    result = experiment(tmp_path, "--bots", "rule", "q_learning_v3")

    assert result.returncode != 0
    assert "missing or malformed" in result.stderr
    assert not (tmp_path / "experiments").exists()
