"""DQN joins Bot Experiments only when explicitly selected with a model."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


pytest.importorskip("torch")
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def command(tmp_path, module, *options):
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, "-m", module, *options], cwd=tmp_path,
        env=environment, capture_output=True, text=True,
    )


def train_model(tmp_path):
    trained = command(
        tmp_path, "snake.sessions.TrainDQN", "--games", "1", "--width", "4",
        "--height", "4", "--max-moves", "4", "--batch-size", "2",
    )
    assert trained.returncode == 0, trained.stderr
    return next((tmp_path / "learning_data" / "dqn_runs").iterdir())


def test_dqn_comparison_uses_shared_seeds_and_records_model(tmp_path):
    trained = command(
        tmp_path, "snake.sessions.TrainDQN", "--games", "1", "--width", "4",
        "--height", "4", "--max-moves", "5",
    )
    assert trained.returncode == 0, trained.stderr
    model = next((tmp_path / "learning_data" / "dqn_runs").iterdir()) / "model.pt"
    compared = command(
        tmp_path, "snake.sessions.RunExperiment", "--bots", "rule", "dqn",
        "--dqn-model", str(model), "--games", "2", "--width", "4",
        "--height", "4", "--max-moves", "5", "--seed", "7",
    )
    assert compared.returncode == 0, compared.stderr
    report = json.loads(next((tmp_path / "experiments").iterdir()).read_text())
    assert report["selected_bot_modes"] == ["rule", "dqn"]
    assert list(report["bots"]) == ["rule", "dqn"]
    assert [game["seed"] for game in report["bots"]["rule"]["games"]] == [7, 8]
    assert [game["seed"] for game in report["bots"]["dqn"]["games"]] == [7, 8]
    assert report["dqn"]["model_path"] == str(model)
    assert report["training_board"]["width"] == 4
    assert report["evaluation_board"]["width"] == 4

    dqn_only = command(
        tmp_path, "snake.sessions.EvaluateDQN", "--model", str(model),
        "--games", "2", "--width", "4", "--height", "4",
        "--max-moves", "5", "--seed", "7",
    )
    assert dqn_only.returncode == 0, dqn_only.stderr
    other_path = next(
        path for path in (tmp_path / "experiments").iterdir()
        if json.loads(path.read_text())["selected_bot_modes"] == ["dqn"]
    )
    dqn_only_report = json.loads(other_path.read_text())
    assert dqn_only_report["bots"]["dqn"]["games"] == report["bots"]["dqn"]["games"]


def test_missing_dqn_model_stops_comparison_before_any_games(tmp_path):
    compared = command(
        tmp_path, "snake.sessions.RunExperiment", "--bots", "rule", "dqn",
        "--games", "1", "--width", "4", "--height", "4", "--max-moves", "5",
    )
    assert compared.returncode != 0
    assert "--dqn-model" in compared.stderr
    assert not (tmp_path / "experiments").exists()


def test_dqn_only_experiment_records_provenance_and_leaves_runtime_data_unchanged(tmp_path):
    run = train_model(tmp_path)
    model = run / "model.pt"
    records = tmp_path / "records" / "game_records.csv"
    records.parent.mkdir()
    records.write_text("watched games\n")
    replay = tmp_path / "replays" / "rule_best.json"
    replay.parent.mkdir()
    replay.write_text("watched replay\n")
    q_table = tmp_path / "learning_data" / "q_table_space_state_v2.json"
    q_table.write_text("{\"existing\": true}\n")
    experiments = tmp_path / "experiments"
    experiments.mkdir()
    existing_report = experiments / "experiment_existing.json"
    existing_report.write_text("{\"existing\": true}\n")
    protected = [*run.iterdir(), records, replay, q_table]
    before = {
        str(path.relative_to(tmp_path)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in protected
    }

    compared = command(
        tmp_path, "snake.sessions.RunExperiment", "--bots", "dqn",
        "--dqn-model", str(model), "--games", "2", "--width", "5",
        "--height", "4", "--tile-size", "13", "--seed", "7",
        "--max-moves", "3",
    )

    assert compared.returncode == 0, compared.stderr
    after = {
        str(path.relative_to(tmp_path)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in protected
    }
    assert after == before
    assert existing_report.read_text() == "{\"existing\": true}\n"
    reports = [path for path in experiments.iterdir() if path != existing_report]
    assert len(reports) == 1
    report = json.loads(reports[0].read_text())
    assert report["schema_version"] == 3
    assert report["selected_bot_modes"] == ["dqn"]
    assert report["board"] == {"width": 5, "height": 4, "tile_size": 13}
    assert report["training_board"] == {"width": 4, "height": 4, "tile_size": 25}
    assert report["evaluation_board"] == report["board"]
    assert report["dqn"]["model_path"] == str(model)
    assert report["dqn"]["model_sha256"] == before[
        f"learning_data/dqn_runs/{run.name}/model.pt"
    ]
    assert report["dqn"]["learning_settings"]["hidden_size"] == 64
    assert report["code"]["git_commit"]
    assert report["python_version"]
    assert report["seeds"] == [7, 8]
    assert [game["seed"] for game in report["bots"]["dqn"]["games"]] == [7, 8]
    assert all(game["moves"] <= 3 for game in report["bots"]["dqn"]["games"])
    assert "mean_score" in report["bots"]["dqn"]["summary"]


def test_repeated_dqn_experiments_reproduce_fixed_seed_games(tmp_path):
    model = train_model(tmp_path) / "model.pt"
    options = (
        "--bots", "dqn", "--dqn-model", str(model), "--games", "2",
        "--width", "4", "--height", "4", "--seed", "7", "--max-moves", "3",
    )

    first = command(tmp_path, "snake.sessions.RunExperiment", *options)
    second = command(tmp_path, "snake.sessions.RunExperiment", *options)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    reports = [
        json.loads(path.read_text())
        for path in sorted((tmp_path / "experiments").iterdir())
    ]
    assert len(reports) == 2
    assert reports[0]["seeds"] == reports[1]["seeds"] == [7, 8]
    assert reports[0]["bots"]["dqn"]["games"] == reports[1]["bots"]["dqn"]["games"]


def test_dqn_preflight_rejects_invalid_model_and_selected_dependencies(tmp_path):
    run = train_model(tmp_path)
    checkpoint = run / "checkpoint.pt"
    missing_model = tmp_path / "missing-model.pt"
    malformed_model = tmp_path / "malformed-model.pt"
    malformed_model.write_bytes(b"not a DQN model")

    for model_path in (missing_model, malformed_model, checkpoint):
        compared = command(
            tmp_path, "snake.sessions.RunExperiment", "--bots", "rule", "dqn",
            "--dqn-model", str(model_path), "--games", "1", "--width", "4",
            "--height", "4", "--max-moves", "2",
        )
        assert compared.returncode != 0
        assert not (tmp_path / "experiments").exists()

    without_table = command(
        tmp_path, "snake.sessions.RunExperiment", "--bots", "q_learning", "dqn",
        "--dqn-model", str(run / "model.pt"), "--games", "1", "--width", "4",
        "--height", "4", "--max-moves", "2",
    )
    assert without_table.returncode != 0
    assert "Q-table" in without_table.stderr
    assert not (tmp_path / "experiments").exists()


def test_dqn_selection_keeps_unsupported_board_as_a_preflight_error(tmp_path):
    model = train_model(tmp_path) / "model.pt"
    compared = command(
        tmp_path, "snake.sessions.RunExperiment", "--bots", "hamiltonian", "dqn",
        "--dqn-model", str(model), "--games", "1", "--width", "3",
        "--height", "3", "--max-moves", "2",
    )

    assert compared.returncode != 0
    assert "Hamiltonian" in compared.stderr
    assert not (tmp_path / "experiments").exists()
