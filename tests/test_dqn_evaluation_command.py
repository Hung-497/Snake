"""Evaluate a saved DQN model through the headless command and report."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


torch = pytest.importorskip("torch")
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
    return next((tmp_path / "learning_data" / "dqn_runs").iterdir()) / "model.pt"


def test_evaluation_is_read_only_and_records_cross_board_identity(tmp_path):
    trained = command(
        tmp_path, "snake.sessions.TrainDQN", "--games", "2", "--width", "4",
        "--height", "4", "--max-moves", "8", "--seed", "9", "--batch-size", "2",
    )
    assert trained.returncode == 0, trained.stderr
    run = next((tmp_path / "learning_data" / "dqn_runs").iterdir())
    model = run / "model.pt"
    records = tmp_path / "records" / "game_records.csv"
    records.parent.mkdir()
    records.write_text("existing watched record\n")
    replay = tmp_path / "replays" / "rule_best.json"
    replay.parent.mkdir()
    replay.write_text("existing replay\n")
    q_table = tmp_path / "learning_data" / "q_table_space_state_v2.json"
    q_table.write_text("{\"existing\": true}\n")
    protected = [*run.iterdir(), records, replay, q_table]
    before = {
        str(path.relative_to(tmp_path)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in protected
    }

    evaluated = command(
        tmp_path, "snake.sessions.EvaluateDQN", "--model", str(model),
        "--games", "2", "--width", "5", "--height", "4", "--max-moves", "8",
        "--seed", "12",
    )
    assert evaluated.returncode == 0, evaluated.stderr
    after = {
        str(path.relative_to(tmp_path)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in protected
    }
    assert after == before
    report_path = next((tmp_path / "experiments").iterdir())
    report = json.loads(report_path.read_text())
    assert report["schema_version"] == 3
    assert report["selected_bot_modes"] == ["dqn"]
    assert report["training_board"]["width"] == 4
    assert report["evaluation_board"]["width"] == 5
    assert report["dqn"]["model_sha256"] == before["learning_data/dqn_runs/" + run.name + "/model.pt"]
    assert report["dqn"]["game_trained"] == 2
    assert report["seeds"] == [12, 13]
    assert [game["seed"] for game in report["bots"]["dqn"]["games"]] == [12, 13]
    assert report["bots"]["dqn"]["summary"]["total_moves"] <= 16


def test_evaluation_requires_a_model_and_rejects_training_checkpoint(tmp_path):
    missing = command(tmp_path, "snake.sessions.EvaluateDQN", "--games", "1")
    assert missing.returncode != 0
    assert "--model" in missing.stderr

    trained = command(
        tmp_path, "snake.sessions.TrainDQN", "--games", "1", "--width", "4",
        "--height", "4", "--max-moves", "4",
    )
    assert trained.returncode == 0, trained.stderr
    checkpoint = next((tmp_path / "learning_data" / "dqn_runs").iterdir()) / "checkpoint.pt"
    rejected = command(
        tmp_path, "snake.sessions.EvaluateDQN", "--model", str(checkpoint),
        "--games", "1", "--width", "4", "--height", "4", "--max-moves", "4",
    )
    assert rejected.returncode != 0
    assert "Wrong DQN artifact type" in rejected.stderr
    assert not (tmp_path / "experiments").exists()


@pytest.mark.parametrize(
    "artifact_kind, expected_error",
    [
        ("missing", "Missing or invalid DQN artifact"),
        ("malformed", "Missing or invalid DQN artifact"),
        ("incompatible", "Incompatible DQN feature or action contract"),
        ("wrong_shape", "Invalid DQN network weights"),
    ],
)
def test_invalid_model_artifacts_fail_before_play_or_report(
    tmp_path, artifact_kind, expected_error,
):
    model = train_model(tmp_path)
    candidate = tmp_path / f"{artifact_kind}.pt"
    if artifact_kind == "malformed":
        candidate.write_bytes(b"not a torch artifact")
    elif artifact_kind == "incompatible":
        artifact = torch.load(model, map_location="cpu", weights_only=True)
        artifact["metadata"] = dict(artifact["metadata"])
        artifact["metadata"]["feature_schema"] = "incompatible"
        torch.save(artifact, candidate)
    elif artifact_kind == "wrong_shape":
        artifact = torch.load(model, map_location="cpu", weights_only=True)
        artifact["online_weights"] = dict(artifact["online_weights"])
        first_weight = next(iter(artifact["online_weights"]))
        artifact["online_weights"][first_weight] = torch.zeros(1)
        torch.save(artifact, candidate)

    rejected = command(
        tmp_path, "snake.sessions.EvaluateDQN", "--model", str(candidate),
        "--games", "1", "--width", "4", "--height", "4", "--max-moves", "4",
    )
    assert rejected.returncode != 0
    assert expected_error in rejected.stderr
    assert not (tmp_path / "experiments").exists()


def test_evaluation_preserves_existing_experiment_report(tmp_path):
    model = train_model(tmp_path)
    experiments = tmp_path / "experiments"
    experiments.mkdir()
    existing = experiments / "experiment_existing.json"
    original = "{\"existing\": true}\n"
    existing.write_text(original)

    evaluated = command(
        tmp_path, "snake.sessions.EvaluateDQN", "--model", str(model),
        "--games", "1", "--width", "4", "--height", "4", "--max-moves", "4",
    )

    assert evaluated.returncode == 0, evaluated.stderr
    assert existing.read_text() == original
    reports = list(experiments.glob("*.json"))
    assert len(reports) == 2
    generated = next(path for path in reports if path != existing)
    assert json.loads(generated.read_text())["selected_bot_modes"] == ["dqn"]
